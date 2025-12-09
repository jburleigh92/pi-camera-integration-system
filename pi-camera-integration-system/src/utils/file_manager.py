"""
File Manager Module
Handles file system operations for captured images
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path


class FileManager:
    """
    Manages capture directory, file naming, and cleanup operations
    """
    
    def __init__(self, config, logger):
        """
        Initialize file manager
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.capture_dir = config['files']['capture_dir']
        self.filename_pattern = config['files']['filename_pattern']
        self.max_age_days = config['files']['max_capture_age_days']
        
        # Ensure capture directory exists
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create required directories if they don't exist"""
        os.makedirs(self.capture_dir, exist_ok=True)
        self.logger.debug(f"Capture directory ready: {self.capture_dir}")
    
    def generate_filename(self, extension='jpg'):
        """
        Generate timestamped filename for capture
        
        Args:
            extension: File extension (default: jpg)
            
        Returns:
            str: Full path to output file
        """
        timestamp = datetime.now()
        filename = timestamp.strftime(self.filename_pattern) + f".{extension}"
        filepath = os.path.join(self.capture_dir, filename)
        return filepath
    
    def verify_file_exists(self, filepath):
        """
        Verify that a file was created and is not empty
        
        Args:
            filepath: Path to file to verify
            
        Returns:
            bool: True if file exists and has content
        """
        if not os.path.exists(filepath):
            self.logger.error(f"File not found: {filepath}")
            return False
        
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            self.logger.error(f"File is empty: {filepath}")
            return False
        
        self.logger.debug(f"File verified: {filepath} ({file_size} bytes)")
        return True
    
    def cleanup_old_captures(self):
        """
        Remove captures older than max_age_days
        
        Returns:
            int: Number of files deleted
        """
        if self.max_age_days <= 0:
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        deleted_count = 0
        
        try:
            for filepath in Path(self.capture_dir).glob('*.jpg'):
                file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    os.remove(filepath)
                    deleted_count += 1
                    self.logger.debug(f"Deleted old capture: {filepath.name}")
            
            if deleted_count > 0:
                self.logger.info(f"Cleanup: Removed {deleted_count} old captures")
        
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
        
        return deleted_count
    
    def get_capture_stats(self):
        """
        Get statistics about stored captures
        
        Returns:
            dict: Statistics including count, total size, oldest/newest
        """
        captures = list(Path(self.capture_dir).glob('*.jpg'))
        
        if not captures:
            return {
                'count': 0,
                'total_size_mb': 0,
                'oldest': None,
                'newest': None
            }
        
        total_size = sum(f.stat().st_size for f in captures)
        mtimes = [datetime.fromtimestamp(f.stat().st_mtime) for f in captures]
        
        return {
            'count': len(captures),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'oldest': min(mtimes).strftime('%Y-%m-%d %H:%M:%S'),
            'newest': max(mtimes).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def archive_captures(self, archive_name=None):
        """
        Create archive of all current captures
        
        Args:
            archive_name: Optional custom archive name
            
        Returns:
            str: Path to created archive or None on failure
        """
        if archive_name is None:
            archive_name = f"captures_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            archive_path = shutil.make_archive(
                archive_name,
                'zip',
                self.capture_dir
            )
            self.logger.info(f"Created archive: {archive_path}")
            return archive_path
        
        except Exception as e:
            self.logger.error(f"Archive creation failed: {e}")
            return None
    
    def delete_capture(self, filepath):
        """
        Delete a specific capture file
        
        Args:
            filepath: Path to file to delete
            
        Returns:
            bool: True if successful
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.debug(f"Deleted: {filepath}")
                return True
            return False
        
        except Exception as e:
            self.logger.error(f"Failed to delete {filepath}: {e}")
            return False
    
    def _get_filename(self, filepath):
        """
        Extract filename from full path
        
        Args:
            filepath: Full file path
            
        Returns:
            str: Filename only
        """
        return os.path.basename(filepath)
