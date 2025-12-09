"""
Camera Interface Module
Handles direct interaction with camera hardware via fswebcam
"""

import os
import subprocess
import time


class CameraInterface:
    """
    Interface to camera hardware using fswebcam
    Handles device validation, warm-up, and capture execution
    """
    
    def __init__(self, config, logger):
        """
        Initialize camera interface
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.device = config['camera']['device']
        self.resolution = config['camera']['resolution']
        self.warmup_delay = config['camera']['warmup_delay']
        self.timeout = config['camera']['capture_timeout']
        self.quality = config['capture']['quality']
        
        # fswebcam flags
        self.fswebcam_flags = config['fswebcam']['flags']
        self.custom_params = config['fswebcam'].get('custom_params', [])
    
    def is_device_present(self):
        """
        Check if camera device exists in /dev
        
        Returns:
            bool: True if device exists
        """
        exists = os.path.exists(self.device)
        
        if exists:
            self.logger.debug(f"Device found: {self.device}")
        else:
            self.logger.error(f"Device not found: {self.device}")
        
        return exists
    
    def check_device_permissions(self):
        """
        Verify read/write permissions on device
        
        Returns:
            bool: True if permissions are adequate
        """
        try:
            # Check if device is readable
            if os.access(self.device, os.R_OK):
                self.logger.debug(f"Device permissions OK: {self.device}")
                return True
            else:
                self.logger.error(f"Insufficient permissions for: {self.device}")
                return False
        
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return False
    
    def list_available_devices(self):
        """
        List all available video devices
        
        Returns:
            list: List of device paths
        """
        devices = []
        for i in range(10):  # Check video0 through video9
            device = f"/dev/video{i}"
            if os.path.exists(device):
                devices.append(device)
        
        return devices
    
    def warm_up(self):
        """
        Wait for camera to initialize after connection
        Prevents "device busy" errors on first capture
        """
        if self.warmup_delay > 0:
            self.logger.debug(f"Warming up camera for {self.warmup_delay}s...")
            time.sleep(self.warmup_delay)
    
    def capture_image(self, output_path):
        """
        Capture single image using fswebcam
        
        Args:
            output_path: Full path where image should be saved
            
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        # Build fswebcam command
        cmd = ['fswebcam']
        cmd.extend(self.fswebcam_flags)
        cmd.extend([
            '-r', self.resolution,
            '-d', self.device,
            '--jpeg', str(self.quality)
        ])
        cmd.extend(self.custom_params)
        cmd.append(output_path)
        
        self.logger.debug(f"Executing: {' '.join(cmd)}")
        
        try:
            # Execute fswebcam with timeout
            result = subprocess.run(
                cmd,
                timeout=self.timeout,
                capture_output=True,
                text=True
            )
            
            # Check for success
            if result.returncode == 0:
                self.logger.debug("fswebcam completed successfully")
                return (True, None)
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                self.logger.debug(f"fswebcam stderr: {error_msg}")
                return (False, error_msg)
        
        except subprocess.TimeoutExpired:
            error_msg = f"Capture timeout after {self.timeout}s"
            self.logger.error(error_msg)
            return (False, error_msg)
        
        except FileNotFoundError:
            error_msg = "fswebcam not found - is it installed?"
            self.logger.error(error_msg)
            return (False, error_msg)
        
        except Exception as e:
            error_msg = f"Capture exception: {str(e)}"
            self.logger.error(error_msg)
            return (False, error_msg)
    
    def test_capture(self):
        """
        Perform test capture to verify camera functionality
        
        Returns:
            bool: True if test successful
        """
        test_file = "/tmp/test_capture.jpg"
        
        self.logger.info("Performing test capture...")
        success, error = self.capture_image(test_file)
        
        if success and os.path.exists(test_file):
            # Verify file is not empty
            if os.path.getsize(test_file) > 0:
                os.remove(test_file)
                self.logger.info("Test capture successful")
                return True
        
        self.logger.error(f"Test capture failed: {error}")
        return False
    
    def get_device_info(self):
        """
        Get information about camera device using v4l2-ctl
        
        Returns:
            dict: Device information or None if unavailable
        """
        try:
            result = subprocess.run(
                ['v4l2-ctl', '--device', self.device, '--all'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {'raw_info': result.stdout}
            
        except Exception as e:
            self.logger.debug(f"Could not get device info: {e}")
        
        return None
    
    def reset_device(self):
        """
        Attempt to reset camera device (requires root)
        This is a placeholder for device reset logic
        
        Returns:
            bool: True if reset attempted
        """
        self.logger.warning("Device reset requested (not implemented)")
        # In production, this might involve:
        # - Unbinding/rebinding USB device
        # - Reloading kernel module
        # - Power cycling via GPIO
        return False
