import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.content_processor import ContentProcessor
from app.ai_client import AIClient
import ebooklib
from ebooklib import epub

@patch("app.content_processor.epub")
def test_process_epub(mock_epub, tmp_path):
    # Setup mock ebook
    mock_book = MagicMock()
    
    # Mock chapters
    mock_item_short = MagicMock()
    mock_item_short.get_content.return_value = b"<html><body><p>Short text</p></body></html>"
    
    mock_item_long = MagicMock()
    # Create long text to pass the length check (> 100 chars)
    long_text = "Data " * 50
    mock_item_long.get_content.return_value = f"<html><body><p>{long_text}</p></body></html>".encode('utf-8')
    
    mock_book.get_items_of_type.return_value = [mock_item_short, mock_item_long]
    
    mock_epub.read_epub.return_value = mock_book
    
    # Mock AI Client
    mock_ai = MagicMock(spec=AIClient)
    mock_ai.enhance_content.return_value = "## Translated Content\n\nThis is narrative prose."
    
    processor = ContentProcessor(ai_client=mock_ai)
    
    # Test path
    input_path = tmp_path / "test.epub"
    
    # Process
    output_path = processor.process_epub(input_path)
    
    assert output_path.name == "[ENHANCED]_test.epub"
    
    # Verify ebooklib read/write calls
    mock_epub.read_epub.assert_called_once_with(str(input_path))
    mock_epub.write_epub.assert_called_once_with(str(output_path), mock_book, {})
    
    # Verify AI was called exactly once (for the long item)
    assert mock_ai.enhance_content.call_count == 1
    
    # Verify short item was NOT modified
    assert mock_item_short.set_content.call_count == 0
    
    # Verify long item WAS modified
    assert mock_item_long.set_content.call_count == 1
    
    # Verify the modified content contains the translated text converted to HTML
    set_content_arg = mock_item_long.set_content.call_args[0][0].decode('utf-8')
    assert "<h2>Translated Content</h2>" in set_content_arg
    assert "This is narrative prose." in set_content_arg

@patch("app.content_processor.epub")
def test_process_epub_read_failure(mock_epub, tmp_path):
    mock_epub.read_epub.side_effect = Exception("Read Error")
    
    processor = ContentProcessor(ai_client=MagicMock())
    with pytest.raises(ValueError, match="Failed to read EPUB: Read Error"):
        processor.process_epub(tmp_path / "test.epub")

def test_physical_epub_roundtrip_integration(tmp_path):
    """
    Physical E2E test without mocking ebooklib to guarantee
    the repackaged EPUB remains structurally sound.
    """
    input_path = tmp_path / "real_test.epub"
    
    # Generate a valid EPUB
    book = epub.EpubBook()
    book.set_identifier("id123456")
    book.set_title("Valid Tech Document")
    book.set_language("en")
    book.add_author("Test Author")

    c1 = epub.EpubHtml(title='Introduction', file_name='chap_01.xhtml', lang='en')
    c1.content = '<html><head></head><body><h1>Intro</h1><p>Short intro.</p></body></html>'
    book.add_item(c1)

    c2 = epub.EpubHtml(title='Technical Data', file_name='chap_02.xhtml', lang='en')
    c2.content = '<html><head></head><body><h1>Data</h1><p>' + ('Long tech text to trigger AI. ' * 10) + '</p></body></html>'
    book.add_item(c2)

    book.toc = (
        epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
        epub.Link('chap_02.xhtml', 'Technical Data', 'data')
    )
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav', c1, c2]

    epub.write_epub(str(input_path), book, {})

    # Mock only the AI client to avoid network calls
    mock_ai = MagicMock(spec=AIClient)
    mock_ai.enhance_content.return_value = "## Translated Content\n\nAI generated text."
    
    processor = ContentProcessor(ai_client=mock_ai)
    output_path = processor.process_epub(input_path)

    # Verification: output file must exist and be readable by ebooklib
    assert output_path.exists()
    
    book_out = epub.read_epub(str(output_path))
    
    # Extract the target chapter by file name and check for AI text
    target_chapter = next((item for item in book_out.get_items_of_type(ebooklib.ITEM_DOCUMENT) if item.get_name() == 'chap_02.xhtml'), None)
    assert target_chapter is not None, "Target chapter chap_02.xhtml not found in output EPUB"
    
    content_02 = target_chapter.get_content().decode('utf-8')
    assert "Translated Content" in content_02
    assert "AI generated text." in content_02
