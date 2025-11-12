"""
Metrics collection system for Sentient Core.

Tracks performance, usage, and system health metrics.
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """Represents a single metric."""
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: str = "gauge"  # gauge, counter, histogram


class MetricsCollector:
    """
    Central metrics collection system.

    Collects and aggregates metrics from all system components.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)

        # Lock for thread safety
        self.lock = threading.Lock()

        # Start time
        self.start_time = time.time()

        logger.info("Metrics collector initialized")

    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric.

        Args:
            name: Metric name
            value: Amount to increment
            labels: Optional labels
        """
        with self.lock:
            key = self._make_key(name, labels)
            self.counters[key] += value

            # Store in history
            metric = Metric(
                name=name,
                value=self.counters[key],
                timestamp=time.time(),
                labels=labels or {},
                metric_type="counter"
            )
            self.metrics[key].append(metric)

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric.

        Args:
            name: Metric name
            value: Gauge value
            labels: Optional labels
        """
        with self.lock:
            key = self._make_key(name, labels)
            self.gauges[key] = value

            # Store in history
            metric = Metric(
                name=name,
                value=value,
                timestamp=time.time(),
                labels=labels or {},
                metric_type="gauge"
            )
            self.metrics[key].append(metric)

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """
        Record a histogram observation.

        Args:
            name: Metric name
            value: Observed value
            labels: Optional labels
        """
        with self.lock:
            key = self._make_key(name, labels)
            self.histograms[key].append(value)

            # Keep only last 1000 observations
            if len(self.histograms[key]) > 1000:
                self.histograms[key] = self.histograms[key][-1000:]

            # Store in history
            metric = Metric(
                name=name,
                value=value,
                timestamp=time.time(),
                labels=labels or {},
                metric_type="histogram"
            )
            self.metrics[key].append(metric)

    def _make_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value."""
        key = self._make_key(name, labels)
        return self.counters.get(key, 0.0)

    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current gauge value."""
        key = self._make_key(name, labels)
        return self.gauges.get(key, 0.0)

    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """
        Get histogram statistics.

        Returns:
            Dictionary with min, max, mean, p50, p95, p99
        """
        import numpy as np

        key = self._make_key(name, labels)
        values = self.histograms.get(key, [])

        if not values:
            return {'count': 0}

        return {
            'count': len(values),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'mean': float(np.mean(values)),
            'p50': float(np.percentile(values, 50)),
            'p95': float(np.percentile(values, 95)),
            'p99': float(np.percentile(values, 99)),
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all current metrics.

        Returns:
            Dictionary of all metrics
        """
        with self.lock:
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {
                    name: self.get_histogram_stats(name)
                    for name in self.histograms.keys()
                },
                'uptime_seconds': time.time() - self.start_time,
            }

    def get_metric_history(self, name: str, labels: Optional[Dict[str, str]] = None, limit: int = 100) -> List[Metric]:
        """
        Get historical values for a metric.

        Args:
            name: Metric name
            labels: Optional labels
            limit: Maximum number of historical values

        Returns:
            List of Metric objects
        """
        key = self._make_key(name, labels)
        history = list(self.metrics.get(key, []))

        return history[-limit:] if limit else history

    def reset_metric(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Reset a specific metric."""
        key = self._make_key(name, labels)

        with self.lock:
            if key in self.counters:
                del self.counters[key]
            if key in self.gauges:
                del self.gauges[key]
            if key in self.histograms:
                del self.histograms[key]
            if key in self.metrics:
                self.metrics[key].clear()

    def reset_all(self):
        """Reset all metrics."""
        with self.lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.metrics.clear()
            self.start_time = time.time()

        logger.info("All metrics reset")

    # Convenience methods for common metrics

    def record_request(self, endpoint: str, duration: float, status: str = "success"):
        """Record an API request."""
        self.increment_counter("requests_total", labels={'endpoint': endpoint, 'status': status})
        self.record_histogram("request_duration_seconds", duration, labels={'endpoint': endpoint})

    def record_model_inference(self, model: str, duration: float, tokens: int = 0):
        """Record a model inference."""
        self.increment_counter("model_inferences_total", labels={'model': model})
        self.record_histogram("model_inference_duration_seconds", duration, labels={'model': model})

        if tokens > 0:
            self.increment_counter("model_tokens_total", value=tokens, labels={'model': model})

    def record_memory_operation(self, operation: str, duration: float):
        """Record a memory system operation."""
        self.increment_counter("memory_operations_total", labels={'operation': operation})
        self.record_histogram("memory_operation_duration_seconds", duration, labels={'operation': operation})

    def record_error(self, component: str, error_type: str):
        """Record an error."""
        self.increment_counter("errors_total", labels={'component': component, 'type': error_type})

    def set_system_metrics(self, cpu_percent: float, memory_percent: float, disk_percent: float):
        """Set system resource metrics."""
        self.set_gauge("system_cpu_percent", cpu_percent)
        self.set_gauge("system_memory_percent", memory_percent)
        self.set_gauge("system_disk_percent", disk_percent)

    def set_component_status(self, component: str, status: int):
        """
        Set component status (1 = healthy, 0 = unhealthy).

        Args:
            component: Component name
            status: Status (1 or 0)
        """
        self.set_gauge("component_status", status, labels={'component': component})


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """
    Get the global metrics collector instance.

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector

    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()

    return _metrics_collector


# Decorator for timing functions
def timed_metric(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """
    Decorator to time function execution and record as metric.

    Args:
        metric_name: Name of the metric
        labels: Optional labels

    Example:
        @timed_metric("my_function_duration")
        def my_function():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                collector = get_metrics_collector()

                metric_labels = labels.copy() if labels else {}
                metric_labels['status'] = status
                metric_labels['function'] = func.__name__

                collector.record_histogram(metric_name, duration, labels=metric_labels)

        return wrapper
    return decorator
