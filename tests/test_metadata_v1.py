import pytest
from app.metadata import MetadataExtractor
from unittest.mock import MagicMock, patch

def test_mobi_extraction_mocked():
    extractor = MetadataExtractor()
    
    with patch('mobi.Mobi') as mock_mobi_class:
        mock_instance = mock_mobi_class.return_value
        mock_instance.author.return_value = b'Stanislav Muller'
        mock_instance.title.return_value = b'Butler Guide'
        
        res = extractor._extract_mobi(MagicMock())
        assert res['author'] == 'Stanislav Muller'
        assert res['title'] == 'Butler Guide'

def test_pdf_extraction_empty():
    extractor = MetadataExtractor()
    with patch('pypdf.PdfReader') as mock_reader:
        mock_reader.return_value.metadata = None
        res = extractor._extract_pdf(MagicMock())
        assert res == {}
