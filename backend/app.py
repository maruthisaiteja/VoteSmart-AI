import os
import re
import logging
from typing import Tuple, Dict, Any, Union
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory, Response
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_talisman import Talisman

# Load environment variables
load_dotenv()

# Google Services: Google Cloud Logging Integration
try:
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.setup_logging()
    logger = logging.getLogger("ElectionAILogger")
    logger.info("Google Cloud Logging successfully initialized.")
except Exception as e:
    # Fallback if no GCP credentials exist in environment
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("ElectionAILogger")
    logger.warning("Local logging fallback. GCP Logging failed to initialize.")

app = Flask(__name__, static_folder='../frontend')

# Security: CORS and Talisman (Security Headers like CSP, HSTS)
CORS(app, resources={r"/api/*": {"origins": "*"}})

csp = {
    'default-src': [
        '\'self\'',
        'https://fonts.googleapis.com',
        'https://fonts.gstatic.com',
        'https://cdnjs.cloudflare.com',
        'https://www.googletagmanager.com',
        'https://maps.googleapis.com',
        'https://maps.google.com'
    ],
    'script-src': [
        '\'self\'',
        '\'unsafe-inline\'', # Required for some gtag and maps logic in this setup
        'https://cdn.jsdelivr.net',
        'https://www.googletagmanager.com',
        'https://maps.googleapis.com'
    ],
    'style-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'https://fonts.googleapis.com',
        'https://cdnjs.cloudflare.com'
    ],
    'frame-src': [
        '\'self\'',
        'https://maps.google.com'
    ]
}
# Content Security Policy disabled in development if needed, but enabled here for strict security
Talisman(app, content_security_policy=csp, force_https=False) # force_https=False for local dev

# Security: Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

chat_session = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash',
            system_instruction="""You are VoteSmart AI, an expert, non-partisan assistant designed to help users understand the election process, timelines, voter registration, and steps to vote. 
            You should be helpful, clear, and easy to understand. Use formatting like bullet points or bold text to make your answers scannable. 
            Do not express political opinions or bias. Focus on the procedural and educational aspects of voting. 
            If someone asks about specific real-world timelines (like 2024 US elections or India elections), provide general accurate information but advise them to check their local official election portals for the most up-to-date details."""
        )
        chat_session = model.start_chat(history=[])
        logger.info("Gemini AI successfully initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini AI: {e}")
else:
    logger.warning("GEMINI_API_KEY not found. Assistant will return mock responses.")

@app.route('/')
def serve_index() -> Response:
    response = send_from_directory(app.static_folder, 'index.html')
    # Efficiency: Add Cache-Control for root HTML (short cache)
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

@app.route('/<path:path>')
def serve_static(path: str) -> Response:
    response = send_from_directory(app.static_folder, path)
    # Efficiency: Add Cache-Control for static assets (long cache)
    if path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.woff2')):
        response.headers['Cache-Control'] = 'public, max-age=86400'
    return response

def sanitize_input(text: str) -> str:
    """Security: Basic input sanitization to prevent injection."""
    if not isinstance(text, str):
        return ""
    # Strip basic HTML tags if any (prevent basic XSS payload reflection)
    return re.sub(r'<[^>]*?>', '', text).strip()

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute") # Rate Limiting to prevent API abuse
def chat() -> Tuple[Response, int]:
    try:
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        raw_message = data.get('message', '')
        language = data.get('language', 'English')

        user_message = sanitize_input(raw_message)

        if not user_message:
            logger.warning("Empty or invalid message received.")
            return jsonify({"error": "Message is required and must be valid text."}), 400

        if not GEMINI_API_KEY or chat_session is None:
            logger.info("Returning mock response (API Key not configured).")
            return jsonify({"reply": "This is a mock response. Please configure your GEMINI_API_KEY in the .env file to enable the real AI assistant."}), 200

        prompt = f"User selected language: {language}. Please reply to the following query ONLY in {language}. Keep the explanation extremely simple, easy to understand for someone with limited education, and use bullet points where helpful. Query: {user_message}"
        
        # Log the interaction (metadata only, not sensitive content)
        logger.info(f"Processing chat request in language: {language}")
        
        response = chat_session.send_message(prompt)
        return jsonify({"reply": response.text}), 200

    except genai.types.generation_types.StopCandidateException as e:
        logger.error(f"Gemini AI generation stopped unexpectedly: {str(e)}")
        return jsonify({"error": "The AI stopped generating the response. Please rephrase."}), 500
    except Exception as e:
        logger.error(f"Error during Gemini API call: {str(e)}")
        return jsonify({"error": "Failed to generate a response from the AI. Please try again later."}), 500

if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
