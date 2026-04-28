document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(sec => sec.classList.remove('active'));
            item.classList.add('active');
            const targetId = item.getAttribute('data-target') + '-section';
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Elements
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const languageSelect = document.getElementById('app-language');
    const micBtn = document.getElementById('mic-btn');
    const mapQuery = document.getElementById('map-query');
    const searchMapBtn = document.getElementById('search-map-btn');
    const gmapIframe = document.getElementById('gmap-iframe');

    // Chat functionality
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        appendMessage('user', message);
        userInput.value = '';
        const loadingId = showLoading();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: message,
                    language: languageSelect.value 
                })
            });

            const data = await response.json();
            document.getElementById(loadingId).remove();

            if (data.error) {
                appendMessage('bot', `Error: ${data.error}`);
            } else {
                appendMessage('bot', data.reply, true);
            }
        } catch (error) {
            document.getElementById(loadingId).remove();
            appendMessage('bot', 'Sorry, I encountered a network error. Please try again.');
        }
    });

    // Map Search Functionality
    if(searchMapBtn && mapQuery) {
        const performSearch = () => {
            const query = mapQuery.value.trim();
            const gmapIframe = document.getElementById('gmap-iframe');
            if(query && gmapIframe) {
                // Use a more robust Maps embed URL format
                const encodedQuery = encodeURIComponent(query);
                gmapIframe.src = `https://maps.google.com/maps?width=100%25&height=600&hl=en&q=${encodedQuery}&t=&z=14&ie=UTF8&iwloc=B&output=embed`;
            }
        };

        searchMapBtn.addEventListener('click', performSearch);
        
        mapQuery.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
    }

    // Speech Recognition (Speech to Text)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        micBtn.addEventListener('click', () => {
            // Set language based on selector (approximate mapping)
            const langMap = {
                'English': 'en-US',
                'Hindi': 'hi-IN',
                'Spanish': 'es-ES',
                'Bengali': 'bn-IN',
                'Tamil': 'ta-IN',
                'Telugu': 'te-IN'
            };
            recognition.lang = langMap[languageSelect.value] || 'en-US';
            
            micBtn.classList.add('recording');
            micBtn.innerHTML = '<i class="fa-solid fa-microphone-lines fa-beat"></i>';
            recognition.start();
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            micBtn.classList.remove('recording');
            micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
            // Automatically submit
            chatForm.dispatchEvent(new Event('submit'));
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            micBtn.classList.remove('recording');
            micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
            alert("Could not recognize speech. Please try again.");
        };
        
        recognition.onend = () => {
            micBtn.classList.remove('recording');
            micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
        };
    } else {
        if(micBtn) micBtn.style.display = 'none'; // Hide if not supported
    }

    function appendMessage(sender, text, isMarkdown = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;
        
        const icon = sender === 'user' ? 'fa-user' : 'fa-robot';
        let contentHtml = text;
        if (isMarkdown && sender === 'bot') {
            contentHtml = marked.parse(text);
        }

        // Add text-to-speech button for bot messages
        let ttsButton = '';
        if (sender === 'bot') {
            // Strip markdown formatting for speech
            const cleanText = text.replace(/[*#_`~]/g, '').replace(/\n/g, '. ');
            const escapedText = cleanText.replace(/'/g, "\\'").replace(/"/g, "&quot;");
            ttsButton = `<button class="tts-btn" onclick="window.speakText('${escapedText}')" title="Listen to message"><i class="fa-solid fa-volume-high"></i></button>`;
        }

        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid ${icon}"></i></div>
            <div class="message-content">${isMarkdown ? contentHtml : escapeHtml(text)}</div>
            ${ttsButton}
        `;
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function showLoading() {
        const id = 'loading-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message';
        msgDiv.id = id;
        
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(unsafe) {
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
});

// Global Text to Speech function
window.speakText = function(text) {
    if (!window.speechSynthesis) {
        alert("Your browser does not support text-to-speech.");
        return;
    }
    
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    const langSelect = document.getElementById('app-language');
    const langMap = {
        'English': 'en-US',
        'Hindi': 'hi-IN',
        'Spanish': 'es-ES',
        'Bengali': 'bn-IN',
        'Tamil': 'ta-IN',
        'Telugu': 'te-IN'
    };
    utterance.lang = langMap[langSelect?.value] || 'en-US';
    utterance.rate = 0.9;
    
    window.speechSynthesis.speak(utterance);
};
