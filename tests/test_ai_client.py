import pytest
from unittest.mock import MagicMock, patch
from app.ai_client import AIClient

@patch("app.ai_client.genai.Client")
def test_enhance_content(mock_genai_client_class):
    # Setup mock
    mock_client_instance = MagicMock()
    mock_genai_client_class.return_value = mock_client_instance
    
    mock_response = MagicMock()
    mock_response.text = "Toto je plynulý text.\n\n## Původní technická data\n- A: 1"
    mock_client_instance.models.generate_content.return_value = mock_response

    # Test
    client = AIClient(api_key="fake-key")
    result = client.enhance_content("- A: 1", target_lang="cs")
    
    assert "Toto je plynulý text" in result
    assert "Původní technická data" in result
    
    # Verify the config was passed correctly
    call_kwargs = mock_client_instance.models.generate_content.call_args.kwargs
    assert call_kwargs['model'] == 'gemini-1.5-flash'
    assert call_kwargs['contents'] == '- A: 1'
    
    config = call_kwargs['config']
    assert "Jsi profesionální technický redaktor" in config.system_instruction

def test_enhance_content_no_client():
    client = AIClient(api_key=None)
    client.client = None # Force none just in case env var is set
    
    result = client.enhance_content("- A: 1")
    assert result == "- A: 1"

@patch("app.ai_client.genai.Client")
def test_enhance_content_exception(mock_genai_client_class):
    mock_client_instance = MagicMock()
    mock_genai_client_class.return_value = mock_client_instance
    mock_client_instance.models.generate_content.side_effect = Exception("API Error")

    client = AIClient(api_key="fake-key")
    result = client.enhance_content("Raw text", target_lang="cs")
    
    # Should fallback to original text on exception
    assert result == "Raw text"
