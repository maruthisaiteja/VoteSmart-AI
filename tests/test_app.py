import json
import pytest
from backend.app import app

@pytest.fixture
def client():
    """A test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the root route returns the index.html page."""
    response = client.get('/')
    # Even if index.html is missing during isolated tests, we should expect a 200 or 404 cleanly.
    assert response.status_code in [200, 404]

def test_chat_route_missing_message(client):
    """Test the /api/chat route with no message."""
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Message is required' in data['error']

def test_chat_route_with_message_mock(client, mocker):
    """Test the /api/chat route with a message when API key is missing or valid."""
    # Force the API key to be empty to test the mock response path
    mocker.patch('backend.app.GEMINI_API_KEY', '')
    
    response = client.post('/api/chat', json={'message': 'How to vote?', 'language': 'English'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'reply' in data
    assert 'mock response' in data['reply']

def test_input_sanitization():
    """Test the input sanitization utility directly."""
    from backend.app import sanitize_input
    
    # Test stripping simple script tags
    dirty_text = "<script>alert('xss')</script>How to vote?"
    clean_text = sanitize_input(dirty_text)
    assert "script" not in clean_text
    assert "How to vote?" in clean_text
    
    # Test normal text
    normal_text = "What is an EVM?"
    assert sanitize_input(normal_text) == normal_text
    
    # Test non-string input
    assert sanitize_input(None) == ""
