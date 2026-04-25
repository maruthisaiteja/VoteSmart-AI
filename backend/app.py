import os
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend')

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Using gemini-2.5-flash for fast and smart responses
    model = genai.GenerativeModel('gemini-2.5-flash',
        system_instruction="""You are VoteSmart AI, an expert, non-partisan assistant designed to help users understand the election process, timelines, voter registration, and steps to vote. 
        You should be helpful, clear, and easy to understand. Use formatting like bullet points or bold text to make your answers scannable. 
        Do not express political opinions or bias. Focus on the procedural and educational aspects of voting. 
        If someone asks about specific real-world timelines (like 2024 US elections or India elections), provide general accurate information but advise them to check their local official election portals for the most up-to-date details."""
    )
    chat_session = model.start_chat(history=[])
else:
    print("WARNING: GEMINI_API_KEY not found. Assistant will return mock responses.")

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    language = data.get('language', 'English')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    if not GEMINI_API_KEY:
        # Mock response if API key is not configured
        return jsonify({"reply": "This is a mock response. Please configure your GEMINI_API_KEY in the .env file to enable the real AI assistant."})

    try:
        prompt = f"User selected language: {language}. Please reply to the following query ONLY in {language}. Keep the explanation extremely simple, easy to understand for someone with limited education, and use bullet points where helpful. Query: {user_message}"
        response = chat_session.send_message(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"Error during Gemini API call: {str(e)}")
        return jsonify({"error": "Failed to generate a response from the AI. Please try again."}), 500

if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
