"""
Tool #11: Monitor Agent

This tool sets up monitoring, logging, and health checks for deployed agents.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger
from pathlib import Path


class MonitoringConfig(BaseModel):
    """Model for monitoring configuration"""
    metrics_enabled: bool = Field(True, description="Enable metrics collection")
    health_check_interval: int = Field(30, description="Health check interval in seconds")
    log_level: str = Field("INFO", description="Logging level")
    alert_on_failure: bool = Field(True, description="Send alerts on failures")


class MonitoringResult(BaseModel):
    """Model for monitoring setup result"""
    success: bool = Field(..., description="Whether monitoring setup succeeded")
    monitoring_files: List[str] = Field(default_factory=list, description="Monitoring config files created")
    metrics_endpoint: Optional[str] = Field(None, description="Metrics endpoint URL")
    dashboard_url: Optional[str] = Field(None, description="Dashboard URL")


class MonitorAgentTool:
    """
    Tool for setting up agent monitoring
    
    Features:
    - Health check endpoints
    - Metrics collection
    - Log aggregation
    - Alert configuration
    """
    
    def __init__(self):
        """Initialize the monitoring tool"""
        logger.info("Initializing MonitorAgentTool")
    
    def setup_monitoring(
        self,
        agent_name: str,
        agent_spec: Dict[str, Any],
        config: MonitoringConfig,
        output_dir: Path
    ) -> MonitoringResult:
        """
        Set up monitoring for an agent
        
        Args:
            agent_name: Name of the agent
            agent_spec: Agent specification
            config: Monitoring configuration
            output_dir: Directory for monitoring configs
            
        Returns:
            MonitoringResult with setup details
        """
        logger.info(f"Setting up monitoring for {agent_name}")
        logger.info(f"  Metrics enabled: {config.metrics_enabled}")
        logger.info(f"  Health check interval: {config.health_check_interval}s")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        monitoring_files = []
        
        # Generate health check script
        health_check = self._generate_health_check(agent_name)
        health_path = output_dir / "health_check.py"
        health_path.write_text(health_check)
        monitoring_files.append(str(health_path))
        logger.info(f"  ✓ Generated: {health_path}")
        
        # Generate metrics collection
        if config.metrics_enabled:
            metrics_code = self._generate_metrics_collector(agent_name, agent_spec)
            metrics_path = output_dir / "metrics.py"
            metrics_path.write_text(metrics_code)
            monitoring_files.append(str(metrics_path))
            logger.info(f"  ✓ Generated: {metrics_path}")
        
        # Generate logging configuration
        logging_config = self._generate_logging_config(agent_name, config.log_level)
        logging_path = output_dir / "logging_config.json"
        logging_path.write_text(logging_config)
        monitoring_files.append(str(logging_path))
        logger.info(f"  ✓ Generated: {logging_path}")
        
        # Generate alert configuration
        if config.alert_on_failure:
            alert_config = self._generate_alert_config(agent_name)
            alert_path = output_dir / "alerts.yml"
            alert_path.write_text(alert_config)
            monitoring_files.append(str(alert_path))
            logger.info(f"  ✓ Generated: {alert_path}")
        
        logger.info(f"✓ Monitoring setup complete")
        logger.info(f"  Files created: {len(monitoring_files)}")
        
        return MonitoringResult(
            success=True,
            monitoring_files=monitoring_files,
            metrics_endpoint=f"http://localhost:9090/metrics/{agent_name.lower()}",
            dashboard_url=None
        )
    
    def _generate_health_check(self, agent_name: str) -> str:
        """Generate health check script"""
        return f'''"""
Health check for {agent_name}
"""

import os
import sys
from loguru import logger


def check_database_connection():
    """Check if database is accessible"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database check failed: {{e}}")
        return False


def check_agent_status():
    """Check if agent is running properly"""
    # Add custom health checks here
    return True


def main():
    """Run all health checks"""
    checks = {{
        "database": check_database_connection(),
        "agent": check_agent_status()
    }}
    
    all_passed = all(checks.values())
    
    if all_passed:
        logger.info("✅ All health checks passed")
        sys.exit(0)
    else:
        logger.error(f"❌ Health checks failed: {{checks}}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
    
    def _generate_metrics_collector(self, agent_name: str, agent_spec: Dict[str, Any]) -> str:
        """Generate metrics collection code"""
        return f'''"""
Metrics collector for {agent_name}
"""

import time
from typing import Dict, Any
from loguru import logger


class MetricsCollector:
    """Collect and expose agent metrics"""
    
    def __init__(self):
        self.metrics = {{
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "execution_time_total": 0.0,
            "last_execution_time": 0.0
        }}
    
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
        
        return {{
            **self.metrics,
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time
        }}
    
    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format"""
        metrics = self.get_metrics()
        
        output = []
        for key, value in metrics.items():
            metric_name = f"{agent_name.lower()}_{{key}}"
            output.append(f"# TYPE {{metric_name}} gauge")
            output.append(f"{{metric_name}} {{value}}")
        
        return "\\n".join(output)


# Global metrics collector instance
metrics_collector = MetricsCollector()
'''
    
    def _generate_logging_config(self, agent_name: str, log_level: str) -> str:
        """Generate logging configuration"""
        import json
        
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": log_level
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "detailed",
                    "filename": f"logs/{agent_name.lower()}.log",
                    "maxBytes": 10485760,
                    "backupCount": 5
                }
            },
            "root": {
                "level": log_level,
                "handlers": ["console", "file"]
            }
        }
        
        return json.dumps(config, indent=2)
    
    def _generate_alert_config(self, agent_name: str) -> str:
        """Generate alert configuration"""
        return f"""# Alert configuration for {agent_name}

alerts:
  - name: high_failure_rate
    condition: failure_rate > 10
    severity: warning
    message: "{{{{ agent_name }}}} failure rate above 10%"
    
  - name: slow_execution
    condition: avg_execution_time > 60
    severity: warning
    message: "{{{{ agent_name }}}} execution time above 60 seconds"
    
  - name: agent_down
    condition: health_check_failed
    severity: critical
    message: "{{{{ agent_name }}}} health check failing"
    
  - name: database_connection_failed
    condition: db_connection_error
    severity: critical
    message: "{{{{ agent_name }}}} cannot connect to database"

notification:
  channels:
    - type: log
      enabled: true
    - type: email
      enabled: false
      recipients: []
    - type: slack
      enabled: false
      webhook_url: ""
"""


def setup_agent_monitoring(
    agent_name: str,
    agent_spec: Dict[str, Any],
    output_dir: Path,
    config: Optional[MonitoringConfig] = None
) -> MonitoringResult:
    """
    Convenience function to setup monitoring
    
    Args:
        agent_name: Agent name
        agent_spec: Agent specification
        output_dir: Output directory
        config: Monitoring configuration
        
    Returns:
        MonitoringResult
    """
    if config is None:
        config = MonitoringConfig()
    
    tool = MonitorAgentTool()
    return tool.setup_monitoring(agent_name, agent_spec, config, output_dir)

