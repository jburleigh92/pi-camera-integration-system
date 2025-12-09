"""
Health Check Module
Monitors system health and camera availability
"""

import time
from datetime import datetime, timedelta


class HealthCheck:
    """
    System health monitoring and metrics tracking
    """
    
    def __init__(self, config, logger, camera_interface):
        """
        Initialize health check system
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
            camera_interface: CameraInterface instance
        """
        self.config = config
        self.logger = logger
        self.camera = camera_interface
        
        self.check_interval = config['health']['check_interval']
        self.max_failures = config['health']['max_consecutive_failures']
        self.alert_on_disconnect = config['health']['alert_on_disconnect']
        
        # Metrics
        self.total_captures = 0
        self.successful_captures = 0
        self.failed_captures = 0
        self.consecutive_failures = 0
        self.last_success_time = None
        self.last_failure_time = None
        self.start_time = datetime.now()
        self.camera_disconnects = 0
        self.last_health_check = None
    
    def record_capture_attempt(self, success):
        """
        Record the result of a capture attempt
        
        Args:
            success: True if capture succeeded
        """
        self.total_captures += 1
        
        if success:
            self.successful_captures += 1
            self.consecutive_failures = 0
            self.last_success_time = datetime.now()
        else:
            self.failed_captures += 1
            self.consecutive_failures += 1
            self.last_failure_time = datetime.now()
    
    def check_camera_health(self):
        """
        Perform health check on camera device
        
        Returns:
            tuple: (status: str, details: dict)
                status: 'healthy', 'degraded', or 'failed'
                details: Additional health information
        """
        self.last_health_check = datetime.now()
        
        # Check device presence
        if not self.camera.is_device_present():
            self.camera_disconnects += 1
            if self.alert_on_disconnect:
                self.logger.log_camera_disconnect()
            
            return ('failed', {
                'reason': 'Camera device not found',
                'device': self.camera.device
            })
        
        # Check permissions
        if not self.camera.check_device_permissions():
            return ('failed', {
                'reason': 'Insufficient device permissions',
                'device': self.camera.device
            })
        
        # Check consecutive failures
        if self.consecutive_failures >= self.max_failures:
            return ('failed', {
                'reason': f'{self.consecutive_failures} consecutive failures',
                'max_allowed': self.max_failures
            })
        
        # Degraded if recent failures
        if self.consecutive_failures > 0:
            return ('degraded', {
                'consecutive_failures': self.consecutive_failures,
                'threshold': self.max_failures
            })
        
        return ('healthy', {})
    
    def get_success_rate(self):
        """
        Calculate capture success rate
        
        Returns:
            float: Success rate as percentage (0-100)
        """
        if self.total_captures == 0:
            return 0.0
        
        return round((self.successful_captures / self.total_captures) * 100, 2)
    
    def get_uptime(self):
        """
        Get system uptime
        
        Returns:
            timedelta: Time since system start
        """
        return datetime.now() - self.start_time
    
    def get_metrics(self):
        """
        Get all health metrics
        
        Returns:
            dict: Complete metrics summary
        """
        uptime = self.get_uptime()
        
        metrics = {
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_formatted': str(uptime).split('.')[0],
            'total_captures': self.total_captures,
            'successful_captures': self.successful_captures,
            'failed_captures': self.failed_captures,
            'success_rate': self.get_success_rate(),
            'consecutive_failures': self.consecutive_failures,
            'camera_disconnects': self.camera_disconnects,
            'last_success': self.last_success_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_success_time else 'Never',
            'last_failure': self.last_failure_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_failure_time else 'Never',
            'last_health_check': self.last_health_check.strftime('%Y-%m-%d %H:%M:%S') if self.last_health_check else 'Never'
        }
        
        return metrics
    
    def print_metrics(self):
        """Print formatted metrics summary"""
        metrics = self.get_metrics()
        
        print("\n" + "="*50)
        print("System Health Metrics")
        print("="*50)
        print(f"Uptime: {metrics['uptime_formatted']}")
        print(f"Total Captures: {metrics['total_captures']}")
        print(f"Success Rate: {metrics['success_rate']}%")
        print(f"Successful: {metrics['successful_captures']}")
        print(f"Failed: {metrics['failed_captures']}")
        print(f"Consecutive Failures: {metrics['consecutive_failures']}")
        print(f"Camera Disconnects: {metrics['camera_disconnects']}")
        print(f"Last Success: {metrics['last_success']}")
        print(f"Last Failure: {metrics['last_failure']}")
        print("="*50 + "\n")
    
    def should_run_health_check(self):
        """
        Determine if enough time has passed for health check
        
        Returns:
            bool: True if health check should run
        """
        if self.last_health_check is None:
            return True
        
        elapsed = (datetime.now() - self.last_health_check).total_seconds()
        return elapsed >= self.check_interval
    
    def reset_metrics(self):
        """Reset all metrics to initial state"""
        self.total_captures = 0
        self.successful_captures = 0
        self.failed_captures = 0
        self.consecutive_failures = 0
        self.last_success_time = None
        self.last_failure_time = None
        self.start_time = datetime.now()
        self.camera_disconnects = 0
        self.last_health_check = None
        
        self.logger.info("Health metrics reset")
    
    def is_system_healthy(self):
        """
        Quick health status check
        
        Returns:
            bool: True if system is operational
        """
        status, _ = self.check_camera_health()
        return status in ['healthy', 'degraded']
