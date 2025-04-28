const chatBox = document.getElementById('chatBox');
const textInput = document.getElementById('textInput');
const imageInput = document.getElementById('imageInput');
const sendButton = document.getElementById('sendButton');
const agentToggle = document.getElementById('agentToggle');
const inputContainer = document.querySelector('.input-container');

let imageBase64 = null;

imageInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imageBase64 = e.target.result;
            addMessage('user', 'Image selected ✓', true);
        };
        reader.readAsDataURL(file);
    }
});

sendButton.addEventListener('click', sendMessage);
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function addLoadingMessage() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-message';
    loadingDiv.innerHTML = `
        <div class="loading-dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    chatBox.appendChild(loadingDiv);
    loadingDiv.scrollIntoView({ behavior: 'smooth' });
    return loadingDiv;
}

function setInputState(disabled) {
    textInput.disabled = disabled;
    sendButton.disabled = disabled;
    imageInput.disabled = disabled;
    inputContainer.classList.toggle('disabled', disabled);
}

async function sendMessage() {
    const text = textInput.value.trim();
    if (!text && !imageBase64) return;

    // Disable inputs while processing
    setInputState(true);

    if (text) addMessage('user', text);
    if (imageBase64) addMessage('user', '<img src="' + imageBase64 + '" class="chat-image">', true);

    const loadingMessage = addLoadingMessage();
    const payload = {
        message: text || "",
        images: imageBase64 ? [imageBase64] : [],
        agent: agentToggle.checked,
        stream: true
    };

    try {
        const response = await fetch('http://localhost:8000/chat/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        // Remove loading message once we start getting response
        loadingMessage.remove();
        const messageElement = addMessage('bot', '');
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            try {
                const lines = chunk.split('\n').filter(line => line.trim());
                for (const line of lines) {
                    try {
                        const jsonData = JSON.parse(line);
                        if (jsonData?.message?.content !== undefined) {
                            const content = jsonData.message.content;
                            if (content) { // Only append non-empty content
                                messageElement.innerHTML += content;
                                messageElement.scrollIntoView({ behavior: 'smooth' });
                            }
                        }
                    } catch (jsonError) {
                        console.warn('Failed to parse JSON:', line, jsonError);
                    }
                }
            } catch (e) {
                console.warn('Failed to process chunk:', chunk, e);
            }
        }
    } catch (error) {
        console.error('Stream error:', error);
        addMessage('bot', 'Sorry, something went wrong.');
    } finally {
        // Re-enable inputs after response is complete
        setInputState(false);
    }

    // Clear inputs
    textInput.value = '';
    imageBase64 = null;
    imageInput.value = '';
}

function addMessage(sender, content, isHtml = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    if (isHtml) {
        messageDiv.innerHTML = content;
    } else {
        messageDiv.textContent = content;
    }
    chatBox.appendChild(messageDiv);
    messageDiv.scrollIntoView({ behavior: 'smooth' });
    return messageDiv;
}

// Add new animation function
async function animateText(element, text) {
    element.innerHTML = text;
    element.scrollIntoView({ behavior: 'smooth' });
    // Add small delay for smoother animation
    await new Promise(resolve => setTimeout(resolve, 10));
}
