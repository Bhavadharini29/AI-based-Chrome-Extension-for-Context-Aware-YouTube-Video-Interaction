document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chatContainer');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const statusDiv = document.getElementById('status');

    let currentVideoId = null;

    // Get current tab URL
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (!tabs || tabs.length === 0) return;
        
        const url = tabs[0].url;
        const videoId = extractVideoId(url);
        
        if (videoId) {
            currentVideoId = videoId;
            statusDiv.textContent = 'Ready';
            statusDiv.className = 'status ready';
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        } else {
            statusDiv.textContent = 'Not a YT Video';
            statusDiv.className = 'status error';
        }
    });

    function extractVideoId(url) {
        if (!url) return null;
        const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/i;
        const match = url.match(regex);
        return match ? match[1] : null;
    }

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        div.textContent = text;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return div;
    }

    function addLoading() {
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `
            <div class="loading-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return div;
    }

    async function handleSend() {
        const text = userInput.value.trim();
        if (!text || !currentVideoId) return;

        addMessage(text, 'user');
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.disabled = true;

        const loadingMsg = addLoading();

        try {
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    video_id: currentVideoId,
                    question: text
                })
            });

            const data = await response.json();
            
            chatContainer.removeChild(loadingMsg);
            
            if (response.ok) {
                addMessage(data.answer, 'bot');
            } else {
                addMessage(`Error: ${data.detail}`, 'system');
            }

        } catch (error) {
            chatContainer.removeChild(loadingMsg);
            addMessage(`Failed to connect to backend server. Make sure your Python FastAPI server is running on port 8000.`, 'system');
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });
});
