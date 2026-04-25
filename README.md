<div align="center">
  <img src="https://img.shields.io/badge/Google-Virtualwars_Hackathon-blue?style=for-the-badge&logo=google" alt="Google Virtualwars">
  <img src="https://img.shields.io/badge/Gemini_2.5_Flash-AI-orange?style=for-the-badge&logo=google" alt="Gemini AI">
  <h1>🗳️ VoteSmart AI</h1>
  <p><strong>The ultimate, highly accessible Election Process Educator built for everyone.</strong></p>
</div>

<br/>

## 🌟 Overview
VoteSmart AI is a smart, dynamic, and hyper-accessible web application designed to educate citizens on the election process, voting timelines, and polling locations. 

Built specifically for the **Google Virtualwars AI Build Challenge** (Vertical: *Election Process Education*), this solution ensures that critical democratic information is accessible to everyone—regardless of their tech-savviness, education level, or native language.

---

## 🎯 Core Features & Innovation

*   **🌍 Universal Multilingual Support**: 
    Breaks down language barriers by dynamically translating and responding natively in **English, Hindi, Spanish, Bengali, Tamil, and Telugu** using the power of Gemini AI.
*   **🎤 Voice Input (Speech-to-Text)**: 
    Typing shouldn't be a requirement to access information. Users can click the microphone icon and simply speak their questions using the browser's native Web Speech API.
*   **🔊 Audio Playback (Text-to-Speech)**: 
    Designed for absolute accessibility. Every AI response features a "Speaker" icon that reads the explanation out loud, empowering illiterate or visually impaired users.
*   **🗺️ Interactive Polling Station Explorer**: 
    Embedded **Google Maps API** allows users to instantly search their city or zip code and visually locate nearby polling centers without leaving the app.
*   **🧠 Educational Prompt Engineering**: 
    Powered by **Google Gemini 2.5 Flash**. The backend AI is strictly instructed to *"Keep explanations extremely simple, easy to understand for someone with limited education, and use bullet points"*—acting as the perfect, non-partisan educational assistant.
*   **✨ Premium, Responsive UI**: 
    A stunning dark-mode aesthetic utilizing glassmorphism, dynamic CSS micro-animations, and intuitive navigation tabs for a "WOW" user experience.

---

## 🏆 Evaluation Focus Areas Addressed

| Metric | How We Nailed It |
| :--- | :--- |
| **Problem Alignment** | Directly tackles "Election Process Education" with dedicated Timeline, Voting Steps, and Smart Assistant tabs. |
| **Google Services** | Deeply integrates **Google Gemini 2.5 Flash** for core intelligence and **Google Maps API** for spatial awareness. |
| **Accessibility** | Voice-in, Voice-out, multi-language support, high contrast ratios, and extremely simple AI language tuning. |
| **Code Quality** | Clean Model-View-Controller separation. A lightweight Python/Flask backend isolates secrets, while vanilla HTML/CSS/JS ensures zero-bloat frontend performance. |
| **Security** | API keys are securely managed via `.env` environment variables and are completely isolated from the client-side. |

---

## 🛠️ Technology Stack

*   **AI Engine**: Google Gemini 2.5 Flash (`google-generativeai` SDK)
*   **Backend**: Python, Flask, python-dotenv
*   **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6)
*   **APIs**: Google Maps Embed API, Web Speech API (SpeechRecognition & SpeechSynthesis)
*   **Formatting**: Marked.js (Markdown rendering)

---

## 🚀 How to Run Locally

### Prerequisites
*   Python 3.10+ installed.
*   A Google Gemini API Key.

### Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Election-ai.git
   cd Election-ai
   ```
2. **Create a `.env` file:**
   Inside the `backend/` directory, create a `.env` file and add your key:
   ```env
   GEMINI_API_KEY=your_actual_google_gemini_api_key_here
   ```
3. **Set up the Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
5. **Run the Server:**
   ```bash
   python backend/app.py
   ```
6. **Access the App:** Open your browser and navigate to `http://127.0.0.1:5000`

---

## ☁️ Google Cloud Deployment (Cloud Run)

To deploy this application to Google Cloud Run, follow these steps:

1. **Create a `Dockerfile`** in the root directory:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 8080
   # Cloud Run injects PORT environment variable
   CMD ["gunicorn", "--bind", "0.0.0.0:8080", "backend.app:app"]
   ```
   *(Note: You will need to add `gunicorn==21.2.0` to your `backend/requirements.txt`)*

2. **Authenticate with Google Cloud CLI:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Deploy directly from source:**
   ```bash
   gcloud run deploy votesmart-ai \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="GEMINI_API_KEY=your_actual_google_gemini_api_key_here"
   ```
4. Click the URL provided in the terminal to view your live, production application!

---
<p align="center"><i>Built with passion for the Google Virtualwars Hackathon.</i></p>
