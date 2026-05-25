import pytest
from app.usb_detector import KindleDetector

def test_kindle_detection_logic():
    detector = KindleDetector()
    # Mocking a list of mounts
    mock_mounts = [
        {"device": "/dev/sdb1", "mount_point": "/media/user/Kindle", "label": "Kindle"},
        {"device": "/dev/sda1", "mount_point": "/", "label": "System"}
    ]
    
    path = detector.find_kindle_path(mock_mounts)
    assert path == "/media/user/Kindle"

def test_no_kindle_found():
    detector = KindleDetector()
    mock_mounts = [{"device": "/dev/sda1", "mount_point": "/", "label": "System"}]
    path = detector.find_kindle_path(mock_mounts)
    assert path is None
