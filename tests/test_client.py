import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from datafog.client import app

runner = CliRunner()

@pytest.fixture
def mock_datafog():
    with patch('datafog.client.DataFog') as mock:
        yield mock

def test_scan_image_no_urls():
    result = runner.invoke(app, ["scan-image"])
    assert result.exit_code == 1
    assert "No image URLs or file paths provided" in result.stdout

@pytest.mark.asyncio
async def test_scan_image_success(mock_datafog):
    mock_instance = mock_datafog.return_value
    mock_instance.run_ocr_pipeline.return_value = ["Mocked result"]
    
    with patch('datafog.client.asyncio.run', new=lambda x: x):
        result = runner.invoke(app, ["scan-image", "http://example.com/image.jpg"])
    
    assert result.exit_code == 0
    assert "OCR Pipeline Results: ['Mocked result']" in result.stdout
    mock_instance.run_ocr_pipeline.assert_called_once_with(image_urls=["http://example.com/image.jpg"])

def test_scan_text_no_texts():
    result = runner.invoke(app, ["scan-text"])
    assert result.exit_code == 1
    assert "No texts provided" in result.stdout

@pytest.mark.asyncio
async def test_scan_text_success(mock_datafog):
    mock_instance = mock_datafog.return_value
    mock_instance.run_text_pipeline.return_value = ["Mocked result"]
    
    with patch('datafog.client.asyncio.run', new=lambda x: x):
        result = runner.invoke(app, ["scan-text", "Sample text"])
    
    assert result.exit_code == 0
    assert "Text Pipeline Results: ['Mocked result']" in result.stdout
    mock_instance.run_text_pipeline.assert_called_once_with(str_list=["Sample text"])

def test_health():
    result = runner.invoke(app, ["health"])
    assert result.exit_code == 0
    assert "DataFog is running" in result.stdout

@patch('datafog.client.get_config')
def test_show_config(mock_get_config):
    mock_get_config.return_value = {"key": "value"}
    result = runner.invoke(app, ["show-config"])
    assert result.exit_code == 0
    assert "{'key': 'value'}" in result.stdout

@patch('datafog.client.SpacyAnnotator.download_model')
def test_download_model(mock_download_model):
    result = runner.invoke(app, ["download-model", "en_core_web_sm"])
    assert result.exit_code == 0
    assert "Model en_core_web_sm downloaded" in result.stdout
    mock_download_model.assert_called_once_with("en_core_web_sm")

@patch('datafog.client.SpacyAnnotator')
def test_show_spacy_model_directory(mock_spacy_annotator):
    mock_instance = mock_spacy_annotator.return_value
    mock_instance.show_model_path.return_value = "/path/to/model"
    result = runner.invoke(app, ["show-spacy-model-directory", "en_core_web_sm"])
    assert result.exit_code == 0
    assert "/path/to/model" in result.stdout

@patch('datafog.client.SpacyAnnotator')
def test_list_spacy_models(mock_spacy_annotator):
    mock_instance = mock_spacy_annotator.return_value
    mock_instance.list_models.return_value = ["model1", "model2"]
    result = runner.invoke(app, ["list-spacy-models"])
    assert result.exit_code == 0
    assert "['model1', 'model2']" in result.stdout

@patch('datafog.client.SpacyAnnotator')
def test_list_entities(mock_spacy_annotator):
    mock_instance = mock_spacy_annotator.return_value
    mock_instance.list_entities.return_value = ["PERSON", "ORG"]
    result = runner.invoke(app, ["list-entities"])
    assert result.exit_code == 0
    assert "['PERSON', 'ORG']" in result.stdout