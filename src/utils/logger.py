"""
Logger Module
Handles all logging operations with file rotation and console output
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class Logger:
    """
    Centralized logging system with file and console output
    Supports log rotation and multiple severity levels
    """
    
    def __init__(self, config):
        """
        Initialize logger with configuration
        
        Args:
            config: Configuration dictionary with logging settings
        """
        self.config = config
        self.log_dir = config['files']['log_dir']
        self.log_file = config['logging']['log_file']
        self.level = config['logging']['level']
        self.console_output = config['logging']['console_output']
        self.max_bytes = config['logging']['max_log_size_mb'] * 1024 * 1024
        self.backup_count = config['logging']['backup_count']
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Setup logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """
        Configure and return logger instance with handlers
        
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger('PiCameraSystem')
        logger.setLevel(getattr(logging, self.level))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler with rotation
        log_path = os.path.join(self.log_dir, self.log_file)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setLevel(getattr(logging, self.level))
        
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.level))
            
            # Console formatter (simpler)
            console_format = logging.Formatter(
                '[%(levelname)s] %(message)s'
            )
            console_handler.setFormatter(console_format)
            logger.addHandler(console_handler)
        
        # File formatter (detailed)
        file_format = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
    
    def log_capture_success(self, filename, attempt=1):
        """
        Log successful image capture
        
        Args:
            filename: Name of captured image file
            attempt: Capture attempt number
        """
        if attempt > 1:
            self.info(f"SUCCESS: Captured {filename} (after {attempt} attempts)")
        else:
            self.info(f"SUCCESS: Captured {filename}")
    
    def log_capture_failure(self, error, attempt, max_attempts):
        """
        Log failed capture attempt
        
        Args:
            error: Error message or exception
            attempt: Current attempt number
            max_attempts: Maximum retry attempts
        """
        self.error(f"Capture failed: {error}. Retry {attempt}/{max_attempts}")
    
    def log_camera_disconnect(self):
        """Log camera disconnect event"""
        self.critical("CRITICAL: Camera disconnected!")
    
    def log_camera_reconnect(self):
        """Log camera reconnection"""
        self.info("Camera reconnected successfully")
    
    def log_health_check(self, status, details=None):
        """
        Log health check result
        
        Args:
            status: Health status (healthy/degraded/failed)
            details: Additional details about health status
        """
        if status == "healthy":
            self.info(f"Health Check: {status}")
        elif status == "degraded":
            self.warning(f"Health Check: {status} - {details}")
        else:
            self.error(f"Health Check: {status} - {details}")
    
    def log_system_start(self):
        """Log system startup"""
        self.info("="*50)
        self.info("Pi Camera Integration System Started")
        self.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info("="*50)
    
    def log_system_stop(self):
        """Log system shutdown"""
        self.info("="*50)
        self.info("Pi Camera Integration System Stopped")
        self.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.info("="*50)
