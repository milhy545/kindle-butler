import os
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MetadataExtractor:
    """
    Extracts author and title metadata from various ebook formats.
    """
    
    def extract(self, file_path: Path) -> Dict[str, str]:
        suffix = file_path.suffix.lower()
        metadata = {"author": "Unknown", "title": file_path.stem}
        
        try:
            if suffix == ".pdf":
                metadata.update(self._extract_pdf(file_path))
            elif suffix in [".azw3", ".mobi"]:
                metadata.update(self._extract_mobi(file_path))
            elif suffix == ".epub":
                metadata.update(self._extract_epub(file_path))
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {file_path}: {e}")
            
        return metadata

    def _extract_pdf(self, file_path: Path) -> Dict[str, str]:
        import pypdf
        info = {}
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                meta = reader.metadata
                if meta:
                    if meta.author:
                        info["author"] = str(meta.author)
                    if meta.title:
                        info["title"] = str(meta.title)
        except Exception as e:
            logger.debug(f"PDF extraction failed for {file_path}: {e}")
        return info

    def _extract_mobi(self, file_path: Path) -> Dict[str, str]:
        from mobi import Mobi
        info = {}
        try:
            book = Mobi(str(file_path))
            book.parse()
            author = book.author()
            title = book.title()
            
            if author:
                info["author"] = author.decode('utf-8', errors='ignore') if isinstance(author, bytes) else str(author)
            if title:
                info["title"] = title.decode('utf-8', errors='ignore') if isinstance(title, bytes) else str(title)
        except Exception as e:
            logger.debug(f"MOBI extraction failed for {file_path}: {e}")
        return info

    def _extract_epub(self, file_path: Path) -> Dict[str, str]:
        import ebooklib
        from ebooklib import epub
        info = {}
        try:
            book = epub.read_epub(str(file_path))
            author = book.get_metadata('DC', 'creator')
            title = book.get_metadata('DC', 'title')
            
            if author:
                # Handle different metadata structures
                if isinstance(author[0], (list, tuple)):
                    info["author"] = author[0][0]
                elif hasattr(author[0], 'get_name'):
                    info["author"] = author[0].get_name()
                else:
                    info["author"] = str(author[0])
                    
            if title:
                info["title"] = title[0][0] if isinstance(title[0], (list, tuple)) else str(title[0])
        except Exception as e:
            logger.debug(f"EPUB extraction failed for {file_path}: {e}")
        return info
