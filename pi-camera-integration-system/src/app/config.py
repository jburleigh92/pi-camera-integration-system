"""
Configuration Module
Loads and validates system configuration from YAML
"""

import os
import yaml


class Config:
    """
    Configuration manager for the camera system
    Loads from YAML and provides validated access to settings
    """
    
    DEFAULT_CONFIG_PATH = "config/default_config.yaml"
    
    def __init__(self, config_path=None):
        """
        Initialize configuration
        
        Args:
            config_path: Optional path to config file (uses default if None)
        """
        if config_path is None:
            config_path = self.DEFAULT_CONFIG_PATH
        
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self):
        """
        Load configuration from YAML file
        
        Returns:
            dict: Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is malformed
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _validate_config(self):
        """
        Validate required configuration fields
        
        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_sections = ['camera', 'capture', 'files', 'logging', 'health']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
        
        # Validate specific critical settings
        if not self.config['camera']['device']:
            raise ValueError("Camera device path is required")
        
        if self.config['capture']['retry_attempts'] < 1:
            raise ValueError("Retry attempts must be at least 1")
    
    def get(self, key, default=None):
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'camera.device')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """
        Set configuration value (runtime only, not persisted)
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_all(self):
        """
        Get entire configuration dictionary
        
        Returns:
            dict: Complete configuration
        """
        return self.config
    
    def save(self, output_path=None):
        """
        Save current configuration to file
        
        Args:
            output_path: Optional output path (uses original path if None)
        """
        if output_path is None:
            output_path = self.config_path
        
        with open(output_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def print_summary(self):
        """Print configuration summary"""
        print("="*50)
        print("Configuration Summary")
        print("="*50)
        print(f"Camera Device: {self.config['camera']['device']}")
        print(f"Resolution: {self.config['camera']['resolution']}")
        print(f"Capture Interval: {self.config['capture']['interval']}s")
        print(f"Retry Attempts: {self.config['capture']['retry_attempts']}")
        print(f"Output Directory: {self.config['files']['capture_dir']}")
        print(f"Log Level: {self.config['logging']['level']}")
        print("="*50)
