"""
Metrics and monitoring utilities.
"""

import logging
import time
from datetime import datetime

import psutil

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects application metrics."""

    def __init__(self):
        self.start_time = time.time()
        self.process = psutil.Process()

    def get_uptime(self) -> float:
        """
        Get application uptime in seconds.

        Returns:
            Uptime in seconds
        """
        return time.time() - self.start_time

    def get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.

        Returns:
            Memory usage in megabytes
        """
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return 0.0

    def get_cpu_percent(self) -> float:
        """
        Get current CPU usage percentage.

        Returns:
            CPU usage percentage
        """
        try:
            return self.process.cpu_percent(interval=0.1)
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return 0.0

    def get_metrics(self) -> dict:
        """
        Get all metrics.

        Returns:
            Dictionary with all metrics
        """
        return {
            "uptime_seconds": self.get_uptime(),
            "memory_usage_mb": self.get_memory_usage(),
            "cpu_percent": self.get_cpu_percent(),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global metrics collector
metrics_collector = MetricsCollector()
