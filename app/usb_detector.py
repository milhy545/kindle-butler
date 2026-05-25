import os
import psutil
from typing import List, Optional, Dict

class KindleDetector:
    """
    Handles detection of Amazon Kindle devices on the system.
    """
    
    KINDLE_LABELS = ["Kindle"]
    
    def get_system_mounts(self) -> List[Dict[str, str]]:
        """
        Returns a list of current system mount points.
        """
        mounts = []
        for part in psutil.disk_partitions(all=False):
            mounts.append({
                "device": part.device,
                "mount_point": part.mountpoint,
                "label": os.path.basename(part.mountpoint)
            })
        return mounts

    def find_kindle_path(self, mounts: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        """
        Searches for a Kindle device in the given or current system mounts.
        """
        if mounts is None:
            mounts = self.get_system_mounts()
            
        for mount in mounts:
            # Check by label or mount point name
            if mount["label"] in self.KINDLE_LABELS:
                return mount["mount_point"]
            if "Kindle" in mount["mount_point"]:
                return mount["mount_point"]
        
        return None

    def wait_for_kindle(self, timeout: int = 30) -> Optional[str]:
        """
        Waits for a Kindle to be plugged in.
        """
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            path = self.find_kindle_path()
            if path:
                return path
            time.sleep(2)
        return None
