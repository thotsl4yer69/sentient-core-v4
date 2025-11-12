"""
Prometheus metrics exporter for Sentient Core.

Exposes metrics in Prometheus format via HTTP endpoint.
"""

import logging
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from .metrics import MetricsCollector, get_metrics_collector

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """
    Exports metrics in Prometheus format.

    Runs an HTTP server that exposes metrics at /metrics endpoint.
    """

    def __init__(
        self,
        port: int = 9090,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """
        Initialize Prometheus exporter.

        Args:
            port: Port to serve metrics on
            metrics_collector: Metrics collector instance
        """
        self.port = port
        self.metrics_collector = metrics_collector or get_metrics_collector()

        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False

        logger.info(f"Prometheus exporter initialized on port {port}")

    def start(self):
        """Start metrics server."""
        if self.running:
            logger.warning("Prometheus exporter already running")
            return

        # Create request handler with access to metrics
        exporter = self

        class MetricsHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/metrics':
                    # Generate Prometheus format metrics
                    metrics_text = exporter._generate_prometheus_metrics()

                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(metrics_text.encode('utf-8'))

                elif self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"status": "healthy"}')

                else:
                    self.send_error(404)

            def log_message(self, format, *args):
                # Suppress default logging
                pass

        # Create and start server
        self.server = HTTPServer(('0.0.0.0', self.port), MetricsHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

        self.running = True
        logger.info(f"Prometheus exporter running on http://0.0.0.0:{self.port}/metrics")

    def stop(self):
        """Stop metrics server."""
        if not self.running:
            return

        if self.server:
            self.server.shutdown()
            self.server.server_close()

        self.running = False
        logger.info("Prometheus exporter stopped")

    def _generate_prometheus_metrics(self) -> str:
        """
        Generate metrics in Prometheus exposition format.

        Returns:
            Metrics as text
        """
        lines = []

        # Add header
        lines.append("# Sentient Core Metrics")
        lines.append("")

        # Counters
        for name, value in self.metrics_collector.counters.items():
            metric_name, labels_str = self._parse_metric_key(name)
            prometheus_name = f"sentient_{metric_name}_total"

            lines.append(f"# TYPE {prometheus_name} counter")
            if labels_str:
                lines.append(f"{prometheus_name}{{{labels_str}}} {value}")
            else:
                lines.append(f"{prometheus_name} {value}")
            lines.append("")

        # Gauges
        for name, value in self.metrics_collector.gauges.items():
            metric_name, labels_str = self._parse_metric_key(name)
            prometheus_name = f"sentient_{metric_name}"

            lines.append(f"# TYPE {prometheus_name} gauge")
            if labels_str:
                lines.append(f"{prometheus_name}{{{labels_str}}} {value}")
            else:
                lines.append(f"{prometheus_name} {value}")
            lines.append("")

        # Histograms
        for name in self.metrics_collector.histograms.keys():
            metric_name, labels_str = self._parse_metric_key(name)
            prometheus_name = f"sentient_{metric_name}"

            stats = self.metrics_collector.get_histogram_stats(metric_name)

            if stats['count'] > 0:
                lines.append(f"# TYPE {prometheus_name} summary")

                lines.append(f"{prometheus_name}_count{{{labels_str}}} {stats['count']}" if labels_str else f"{prometheus_name}_count {stats['count']}")
                lines.append(f"{prometheus_name}_sum{{{labels_str}}} {stats['mean'] * stats['count']}" if labels_str else f"{prometheus_name}_sum {stats['mean'] * stats['count']}")

                # Quantiles
                for quantile, value in [("0.5", stats['p50']), ("0.95", stats['p95']), ("0.99", stats['p99'])]:
                    q_label = f"quantile=\"{quantile}\""
                    if labels_str:
                        full_labels = f"{labels_str},{q_label}"
                    else:
                        full_labels = q_label
                    lines.append(f"{prometheus_name}{{{full_labels}}} {value}")

                lines.append("")

        # Uptime
        uptime = self.metrics_collector.get_all_metrics()['uptime_seconds']
        lines.append("# TYPE sentient_uptime_seconds gauge")
        lines.append(f"sentient_uptime_seconds {uptime}")

        return "\n".join(lines)

    def _parse_metric_key(self, key: str) -> tuple:
        """
        Parse metric key into name and labels.

        Args:
            key: Metric key (e.g., "requests{endpoint=/api,status=success}")

        Returns:
            Tuple of (metric_name, labels_string)
        """
        if '{' in key:
            name, labels_part = key.split('{', 1)
            labels_str = labels_part.rstrip('}')
            return name, labels_str
        else:
            return key, ""


if __name__ == "__main__":
    # Test exporter
    logging.basicConfig(level=logging.INFO)

    # Create metrics
    collector = get_metrics_collector()

    collector.increment_counter("test_counter")
    collector.set_gauge("test_gauge", 42.5)
    collector.record_histogram("test_duration", 0.123)

    # Start exporter
    exporter = PrometheusExporter(port=9090)
    exporter.start()

    print("Metrics available at http://localhost:9090/metrics")
    print("Press Ctrl+C to stop")

    try:
        import time
        while True:
            time.sleep(1)
            collector.increment_counter("test_counter")
    except KeyboardInterrupt:
        exporter.stop()
