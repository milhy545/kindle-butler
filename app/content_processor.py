import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

import ebooklib
from ebooklib import epub
from app.ai_client import AIClient
from pathlib import Path
import markdown

import uuid

class ContentProcessor:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def _fix_ebooklib_toc_uids(self, toc):
        """
        Fixes a known bug in ebooklib where read_epub sets Link.uid to None.
        This causes lxml to crash during write_epub.
        """
        for item in toc:
            if isinstance(item, epub.Link):
                if item.uid is None:
                    # Generate a unique ID if it's missing to satisfy lxml writing
                    item.uid = str(uuid.uuid4())
            elif isinstance(item, tuple) and len(item) == 2:
                # Handle nested sections (Section, [Links...])
                if isinstance(item[0], epub.Section) and getattr(item[0], 'href', None):
                    # Sections themselves don't strictly require uid, but their children might
                    pass
                self._fix_ebooklib_toc_uids(item[1])

    def process_epub(self, file_path: Path, target_lang: str = "cs", progress=None) -> Path:
        """
        Reads an EPUB, extracts HTML chapters, translates/enhances the text using AI,
        and repacks it into a new '[ENHANCED]_<filename>.epub'.
        """
        try:
            # ebooklib uses print internally for some warnings, suppress standard stdout if needed, 
            # but we'll let it be for now.
            book = epub.read_epub(str(file_path))
        except Exception as e:
            raise ValueError(f"Failed to read EPUB: {e}")
        
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        
        task = None
        if progress:
            task = progress.add_task(f"Enhancing {file_path.name}...", total=len(items))

        for item in items:
            content = item.get_content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract text
            text = soup.get_text(separator='\n')
            
            # Skip very short fragments like title pages or empty TOC items
            if len(text.strip()) < 100:
                if progress and task is not None:
                    progress.advance(task)
                continue
                
            # Enhance content via AI
            enhanced_md = self.ai_client.enhance_content(text, target_lang=target_lang)
            
            # Convert the returned Markdown into HTML
            enhanced_html = markdown.markdown(enhanced_md)
            
            # Replace the body content
            if soup.body:
                soup.body.clear()
                soup.body.append(BeautifulSoup(enhanced_html, 'html.parser'))
            else:
                # If no body, just wrap it
                soup = BeautifulSoup(f"<html><body>{enhanced_html}</body></html>", 'html.parser')
            
            # Ensure the item retains its original ID when saving back
            original_id = item.id
            item.set_content(str(soup).encode('utf-8'))
            if original_id:
                item.id = original_id
            
            if progress and task is not None:
                progress.advance(task)
                
        # Fix missing UIDs caused by ebooklib's read parsing before saving back
        self._fix_ebooklib_toc_uids(book.toc)
                
        output_path = file_path.with_name(f"[ENHANCED]_{file_path.name}")
        epub.write_epub(str(output_path), book, {})
        return output_path
