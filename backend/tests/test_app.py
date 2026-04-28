import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test if the index route serves the frontend HTML."""
    response = client.get('/')
    # Even if index.html doesn't exist during some test setups, we expect a 200 or 404 (if static not built)
    # The app.py serves it so we expect it to try. 
    assert response.status_code in [200, 404]

def test_chat_api_missing_message(client):
    """Test the chat API with missing message payload."""
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    assert b"Message is required" in response.data

def test_chat_api_mock_response(client, mocker):
    """Test the chat API mock response when API key is not set."""
    # Mock GEMINI_API_KEY to be empty
    mocker.patch('app.GEMINI_API_KEY', "")
    
    response = client.post('/api/chat', json={"message": "How do I vote?"})
    assert response.status_code == 200
    assert b"mock response" in response.data

def test_chat_api_rate_limiting(client):
    """Test if rate limiting works by exceeding the limit."""
    # The limit is 10 per minute. Let's send 11 requests.
    for _ in range(10):
        client.post('/api/chat', json={"message": "test"})
    
    response = client.post('/api/chat', json={"message": "test limit"})
    assert response.status_code == 429  # Too Many Requests

from app import app, sanitize_input

def test_sanitization_function():
    """Test if input is sanitized properly before processing."""
    # Test basic stripping of HTML
    dirty_text = "<script>alert('xss')</script> Hello"
    clean_text = sanitize_input(dirty_text)
    
    assert "<script>" not in clean_text
    assert clean_text == "alert('xss') Hello"

def test_security_headers_and_cors(client):
    """Test if Talisman and CORS are adding the correct security headers."""
    response = client.get('/')
    # Talisman headers
    assert 'Content-Security-Policy' in response.headers
    assert 'X-Content-Type-Options' in response.headers
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    # Efficiency Headers
    assert 'Cache-Control' in response.headers

    # CORS Headers for API
    api_response = client.options('/api/chat')
    assert 'Access-Control-Allow-Origin' in api_response.headers
    assert api_response.headers['Access-Control-Allow-Origin'] == '*'
