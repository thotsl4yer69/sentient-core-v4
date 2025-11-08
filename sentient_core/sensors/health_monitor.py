"""
System Health Monitoring & Diagnostics.

Monitors hardware and software health for early problem detection.
"""

import threading
import logging
import time
import psutil
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    Monitors system health and performance metrics.

    Tracks:
    - CPU usage
    - Memory usage
    - Disk usage
    - Temperature
    - Network connectivity
    - Process health
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize health monitor.

        Args:
            config: Configuration object
        """
        self.config = config or {}
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Health data
        self.health_data: Dict[str, Any] = {}
        self.alerts: List[Dict[str, Any]] = []

        # Monitoring parameters
        self.update_interval = self.config.get('health_update_interval', 5)  # seconds

        # Thresholds
        self.cpu_threshold = self.config.get('cpu_threshold', 90)  # %
        self.memory_threshold = self.config.get('memory_threshold', 90)  # %
        self.disk_threshold = self.config.get('disk_threshold', 90)  # %
        self.temp_threshold = self.config.get('temp_threshold', 80)  # °C

        logger.info("Health Monitor initialized")

    def start(self):
        """Start health monitoring."""
        if self.running:
            logger.warning("Health Monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("Health Monitor started")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Collect health metrics
                self._collect_metrics()

                # Check for alerts
                self._check_alerts()

                time.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(self.update_interval)

    def _collect_metrics(self):
        """Collect system health metrics."""
        self.health_data = {
            'timestamp': datetime.now().isoformat(),
            'cpu': self._get_cpu_metrics(),
            'memory': self._get_memory_metrics(),
            'disk': self._get_disk_metrics(),
            'temperature': self._get_temperature(),
            'network': self._get_network_metrics(),
            'uptime': self._get_uptime()
        }

    def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU metrics."""
        return {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'per_core': psutil.cpu_percent(interval=1, percpu=True),
            'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }

    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory metrics."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent
        }

    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk metrics."""
        disk = psutil.disk_usage('/')

        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }

    def _get_temperature(self) -> Optional[float]:
        """Get CPU temperature (Raspberry Pi specific)."""
        try:
            # Try Pi-specific thermal zone
            thermal_file = Path('/sys/class/thermal/thermal_zone0/temp')
            if thermal_file.exists():
                with open(thermal_file, 'r') as f:
                    temp = float(f.read()) / 1000.0
                    return temp

            # Fallback to psutil sensors (if available)
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get first available temperature
                    for name, entries in temps.items():
                        if entries:
                            return entries[0].current

            return None

        except Exception as e:
            logger.debug(f"Temperature read error: {e}")
            return None

    def _get_network_metrics(self) -> Dict[str, Any]:
        """Get network metrics."""
        net_io = psutil.net_io_counters()

        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout
        }

    def _get_uptime(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - psutil.boot_time()

    def _check_alerts(self):
        """Check for alert conditions."""
        alerts = []

        # CPU alert
        cpu_percent = self.health_data.get('cpu', {}).get('percent', 0)
        if cpu_percent > self.cpu_threshold:
            alerts.append({
                'type': 'cpu_high',
                'severity': 'warning',
                'message': f'CPU usage high: {cpu_percent:.1f}%',
                'timestamp': datetime.now().isoformat()
            })

        # Memory alert
        mem_percent = self.health_data.get('memory', {}).get('percent', 0)
        if mem_percent > self.memory_threshold:
            alerts.append({
                'type': 'memory_high',
                'severity': 'warning',
                'message': f'Memory usage high: {mem_percent:.1f}%',
                'timestamp': datetime.now().isoformat()
            })

        # Disk alert
        disk_percent = self.health_data.get('disk', {}).get('percent', 0)
        if disk_percent > self.disk_threshold:
            alerts.append({
                'type': 'disk_high',
                'severity': 'warning',
                'message': f'Disk usage high: {disk_percent:.1f}%',
                'timestamp': datetime.now().isoformat()
            })

        # Temperature alert
        temp = self.health_data.get('temperature')
        if temp and temp > self.temp_threshold:
            alerts.append({
                'type': 'temperature_high',
                'severity': 'critical',
                'message': f'Temperature high: {temp:.1f}°C',
                'timestamp': datetime.now().isoformat()
            })

        # Log alerts
        for alert in alerts:
            if alert['severity'] == 'critical':
                logger.error(alert['message'])
            else:
                logger.warning(alert['message'])

        # Store alerts
        self.alerts.extend(alerts)

        # Keep only recent alerts (last hour)
        now = datetime.now()
        self.alerts = [
            a for a in self.alerts
            if (now - datetime.fromisoformat(a['timestamp'])).total_seconds() < 3600
        ]

    def get_health(self) -> Dict[str, Any]:
        """
        Get current health status.

        Returns:
            Health status dictionary
        """
        return self.health_data.copy()

    def get_alerts(self) -> List[Dict[str, Any]]:
        """
        Get recent alerts.

        Returns:
            List of alert dictionaries
        """
        return self.alerts.copy()

    def get_health_score(self) -> float:
        """
        Compute overall health score (0.0 to 1.0).

        Returns:
            Health score
        """
        if not self.health_data:
            return 0.0

        score = 1.0

        # Penalize for high CPU
        cpu_percent = self.health_data.get('cpu', {}).get('percent', 0)
        if cpu_percent > 70:
            score -= (cpu_percent - 70) / 100

        # Penalize for high memory
        mem_percent = self.health_data.get('memory', {}).get('percent', 0)
        if mem_percent > 70:
            score -= (mem_percent - 70) / 100

        # Penalize for high temperature
        temp = self.health_data.get('temperature')
        if temp and temp > 60:
            score -= (temp - 60) / 100

        # Penalize for active alerts
        critical_alerts = [a for a in self.alerts if a['severity'] == 'critical']
        score -= len(critical_alerts) * 0.2

        return max(0.0, min(1.0, score))

    def stop(self):
        """Stop health monitoring."""
        self.running = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        logger.info("Health Monitor stopped")
