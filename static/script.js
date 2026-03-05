document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    function addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);

        // Very basic markdown handling for code blocks and line breaks
        let formattedContent = content;

        // Handle code blocks first
        formattedContent = formattedContent.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

        // Handle inline code
        formattedContent = formattedContent.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Handle line breaks (only outside of pre/code blocks) - simple version
        formattedContent = formattedContent.split('\n').map(line => line.trim() ? `${line}<br>` : '<br>').join('');

        // Clean up extra br tags created around pre elements
        formattedContent = formattedContent.replace(/<br>\s*<pre>/g, '<pre>').replace(/<\/pre>\s*<br>/g, '</pre>');

        messageDiv.innerHTML = formattedContent;

        chatHistory.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Display user message
        addMessage(message, 'user');
        userInput.value = '';
        userInput.focus();

        // Add a loading indicator
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('message', 'bot');
        loadingDiv.id = loadingId;
        loadingDiv.innerHTML = '<p class="typing-indicator">Thinking...</p>';
        chatHistory.appendChild(loadingDiv);
        scrollToBottom();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: message })
            });

            const data = await response.json();

            // Remove loading indicator
            document.getElementById(loadingId).remove();

            // Display bot response
            addMessage(data.response, 'bot');

        } catch (error) {
            console.error('Error:', error);
            const loadingEl = document.getElementById(loadingId);
            if (loadingEl) loadingEl.remove();
            addMessage('Sorry, an error occurred while connecting to the server. Please ensure the backend is running.', 'bot');
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Initial focus
    userInput.focus();
});
