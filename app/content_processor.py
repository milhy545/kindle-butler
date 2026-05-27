import warnings
from pathlib import Path
import tempfile
import uuid
import re
from typing import Optional

import ebooklib
import markdown
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from ebooklib import epub

from app.ai_client import AIClient

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

class ContentProcessor:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def _strip_unsafe_html_from_markdown(self, content: str) -> str:
        content = re.sub(
            r"<(script|iframe|object|embed|form|link|style)[^>]*>.*?</\1>",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )
        return re.sub(r"on\w+\s*=\s*['\"][^'\"]*['\"]", "", content, flags=re.IGNORECASE)

    def _sanitize_ai_html(self, content: str) -> str:
        soup = BeautifulSoup(markdown.markdown(content), "html.parser")
        for tag in soup(["script", "iframe", "object", "embed", "form", "link", "style"]):
            tag.decompose()
        for tag in soup.find_all(True):
            for attr in list(tag.attrs):
                if attr.lower().startswith("on"):
                    del tag.attrs[attr]
        return str(soup)

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

    def translate_markdown(self, md_path: Path, target_lang: str = "cs") -> Optional[Path]:
        """
        Reads a Markdown file, translates/enhances it using AI, and saves it to a temporary file.
        Returns None if translation fails.
        """
        if not self.ai_client:
            return None
            
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # For very large files, we might need chunking, but for manuals it should fit
            enhanced_md = self.ai_client.enhance_content(content, target_lang=target_lang)
            if enhanced_md is None:
                return None
            
            enhanced_md = self._strip_unsafe_html_from_markdown(enhanced_md)
            
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                suffix=md_path.suffix,
                prefix=f"{md_path.stem}-translated-",
                dir=md_path.parent,
                delete=False,
            ) as f:
                f.write(enhanced_md)
                output_path = Path(f.name)
            return output_path
        except Exception as e:
            print(f"Error during translation: {e}")
            return None

    def convert_markdown_to_epub(self, md_path: Path, output_path: Path, title: str, author: str) -> bool:
        """
        Converts a Markdown file to an e-book format (EPUB/AZW3) using ebook-convert.
        """
        import subprocess  # nosec B404
        try:
            input_path = md_path.resolve()
            converted_path = output_path.resolve()
            cmd = [
                "ebook-convert",
                str(input_path),
                str(converted_path),
                "--title", title,
                "--authors", author,
                "--chapter", "//*[name()='h1' or name()='h2']",
                "--level1-toc", "//h:h1",
                "--level2-toc", "//h:h2"
            ]
            # Use format specific flags only if output is EPUB
            if output_path.suffix.lower() == ".epub":
                cmd.append("--no-default-epub-cover")
            
            subprocess.run(cmd, check=True, capture_output=True)  # nosec B603
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e.stderr.decode()}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

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
            if enhanced_md is None:
                if progress and task is not None:
                    progress.advance(task)
                continue
            
            # Convert the returned Markdown into HTML
            enhanced_html = self._sanitize_ai_html(enhanced_md)
            
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
