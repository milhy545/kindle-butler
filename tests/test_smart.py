import pytest
from app.metadata import MetadataExtractor
from app.ai_client import AIClient
from unittest.mock import MagicMock

def test_ai_normalization_fallback():
    # Test that it returns raw data if no API key
    client = AIClient(api_key=None)
    result = client.normalize_metadata("Muller, Stanislav", "Kindle Butler Docs")
    assert result["author"] == "Muller, Stanislav"

def test_metadata_extraction_logic():
    extractor = MetadataExtractor()
    # Logic test without real files
    meta = extractor.extract(MagicMock(suffix=".txt", stem="Test_File"))
    assert meta["author"] == "Unknown"
    assert meta["title"] == "Test_File"
