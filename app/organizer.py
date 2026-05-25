import os
import shutil
import hashlib
import re
from pathlib import Path
from typing import List

class KindleOrganizer:
    """
    Handles scanning, backing up, and organizing files on the Kindle device.
    """
    
    def __init__(self, kindle_root: str):
        self.root = Path(kindle_root)
        self.docs_path = self.root / "documents"
        self.backup_path = self.root / ".butler_backup"

    def _sanitize_path_component(self, name: str) -> str:
        """
        Sanitizes a string to be used as a directory name.
        Prevents path traversal and unusual characters.
        """
        if not name:
            return "Unknown"
            
        # Replace common path separators and problematic characters with underscore
        name = name.replace("/", "_").replace("\\", "_").replace(".", "_").replace("\0", "")
        
        # Remove control characters
        name = re.sub(r'[\x00-\x1f\x7f]', '', name)
        
        # Strip leading/trailing underscores and spaces
        name = name.strip("_ ")
        
        # If empty after stripping, return Unknown
        if not name:
            return "Unknown"
            
        # Limit length to 100 chars
        return name[:100]

    def scan_documents(self) -> List[Path]:
        """
        Recursively scans the documents folder for ebook files.
        """
        if not self.docs_path.exists():
            return []
            
        extensions = {".azw3", ".kfx", ".mobi", ".pdf", ".epub"}
        return [p for p in self.docs_path.rglob("*") if p.suffix.lower() in extensions]

    def create_backup(self, file_path: Path) -> Path:
        """
        Creates a copy of the file in the backup directory before modification.
        Uses a hash of the path to avoid collisions.
        """
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create a unique but readable filename
        path_hash = hashlib.sha256(str(file_path).encode()).hexdigest()[:8]
        safe_name = f"{path_hash}_{file_path.name}"
        
        target_backup = self.backup_path / safe_name
        shutil.copy2(str(file_path), str(target_backup))
        
        # Backup associated .sdr folder if it exists
        # Kindle uses two naming conventions: Book.sdr or Book.ext.sdr
        sdr_variants = [
            file_path.with_suffix(".sdr"),
            file_path.with_suffix(file_path.suffix + ".sdr")
        ]
        for sdr_folder in sdr_variants:
            if sdr_folder.exists() and sdr_folder.is_dir():
                target_sdr = self.backup_path / f"{path_hash}_{sdr_folder.name}"
                if target_sdr.exists():
                    shutil.rmtree(str(target_sdr))
                shutil.copytree(str(sdr_folder), str(target_sdr))
            
        return target_backup

    def get_target_path(self, file_path: Path, author: str) -> Path:
        """
        Calculates the intended target path for a file.
        """
        safe_author = self._sanitize_path_component(author)
        author_dir = self.docs_path / safe_author
        return author_dir / file_path.name

    def organize_file(self, file_path: Path, author: str):
        """
        Moves a file into a folder named after the author.
        """
        target_path = self.get_target_path(file_path, author)
        
        # Don't move if it's already in the right place
        if file_path.resolve() == target_path.resolve():
            return
            
        # Ensure author dir exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # If target already exists, back it up before overwriting
        if target_path.exists():
            self.create_backup(target_path)
            
        shutil.move(str(file_path), str(target_path))
        
        # Move associated .sdr folder if it exists
        sdr_variants = [
            file_path.with_suffix(".sdr"),
            file_path.with_suffix(file_path.suffix + ".sdr")
        ]
        for sdr_folder in sdr_variants:
            if sdr_folder.exists() and sdr_folder.is_dir():
                target_sdr = target_path.parent / sdr_folder.name
                if target_sdr.exists():
                    shutil.rmtree(str(target_sdr))
                shutil.move(str(sdr_folder), str(target_sdr))
