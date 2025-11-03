"""
Metrics collector for CalcAgent
"""

import time
from typing import Dict, Any
from loguru import logger


class MetricsCollector:
    """Collect and expose agent metrics"""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "execution_time_total": 0.0,
            "last_execution_time": 0.0
        }
    
    def record_request(self, success: bool, duration: float):
        """Record a request execution"""
        self.metrics["requests_total"] += 1
        
        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_failed"] += 1
        
        self.metrics["execution_time_total"] += duration
        self.metrics["last_execution_time"] = duration
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        success_rate = (
            self.metrics["requests_success"] / self.metrics["requests_total"] * 100
            if self.metrics["requests_total"] > 0
            else 0.0
        )
        
        avg_execution_time = (
            self.metrics["execution_time_total"] / self.metrics["requests_total"]
            if self.metrics["requests_total"] > 0
            else 0.0
        )
        
        return {
            **self.metrics,
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time
        }
    
    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        metrics = self.get_metrics()
        
        output = []
        for key, value in metrics.items():
            metric_name = f"calcagent_{key}"
            output.append(f"# TYPE {metric_name} gauge")
            output.append(f"{metric_name} {value}")
        
        return "\n".join(output)


# Global metrics collector instance
metrics_collector = MetricsCollector()
