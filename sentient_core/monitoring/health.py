"""
Health monitoring system for Sentient Core.

Tracks component health and system status.
"""

import logging
import psutil
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status of a component."""
    name: str
    status: HealthStatus
    message: str
    metrics: Dict[str, Any]


class HealthMonitor:
    """
    Monitors system and component health.
    """

    def __init__(self):
        """Initialize health monitor."""
        self.component_health: Dict[str, ComponentHealth] = {}

        logger.info("Health monitor initialized")

    def update_component_health(
        self,
        component: str,
        status: HealthStatus,
        message: str = "",
        metrics: Dict[str, Any] = None
    ):
        """
        Update health status for a component.

        Args:
            component: Component name
            status: Health status
            message: Status message
            metrics: Component metrics
        """
        self.component_health[component] = ComponentHealth(
            name=component,
            status=status,
            message=message,
            metrics=metrics or {}
        )

    def get_component_health(self, component: str) -> ComponentHealth:
        """
        Get health status for a component.

        Args:
            component: Component name

        Returns:
            ComponentHealth instance
        """
        return self.component_health.get(
            component,
            ComponentHealth(
                name=component,
                status=HealthStatus.UNKNOWN,
                message="No health data",
                metrics={}
            )
        )

    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health.

        Returns:
            System health dictionary
        """
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        system_metrics = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / (1024 * 1024),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024 * 1024 * 1024),
        }

        # Determine overall status
        overall_status = HealthStatus.HEALTHY

        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            overall_status = HealthStatus.DEGRADED

        # Check component health
        unhealthy_components = [
            name for name, health in self.component_health.items()
            if health.status == HealthStatus.UNHEALTHY
        ]

        if unhealthy_components:
            overall_status = HealthStatus.UNHEALTHY

        degraded_components = [
            name for name, health in self.component_health.items()
            if health.status == HealthStatus.DEGRADED
        ]

        if degraded_components and overall_status == HealthStatus.HEALTHY:
            overall_status = HealthStatus.DEGRADED

        return {
            'status': overall_status.value,
            'system_metrics': system_metrics,
            'components': {
                name: {
                    'status': health.status.value,
                    'message': health.message,
                    'metrics': health.metrics
                }
                for name, health in self.component_health.items()
            },
            'unhealthy_components': unhealthy_components,
            'degraded_components': degraded_components,
        }

    def is_healthy(self) -> bool:
        """
        Check if system is healthy.

        Returns:
            True if healthy
        """
        health = self.get_system_health()
        return health['status'] == HealthStatus.HEALTHY.value
