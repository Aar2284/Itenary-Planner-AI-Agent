let sessionId = 'session_' + Date.now();

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    appendMessage('user', message);
    input.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: sessionId })
        });
        const data = await response.json();
        if (data.session_id) sessionId = data.session_id;
        appendMessage('assistant', data.response);
    } catch (error) {
        appendMessage('assistant', 'Sorry, something went wrong. Please try again.');
    }
}

function appendMessage(role, text) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.innerHTML = `<p>${text}</p>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});