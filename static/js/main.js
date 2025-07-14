// WebSocket connection management
let chatSocket = null;
let conversationId = null;

// Initialize WebSocket connection
function initializeWebSocket(convId) {
    if (chatSocket) {
        chatSocket.close();
    }
    
    conversationId = convId;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${conversationId}/`;
    
    chatSocket = new WebSocket(wsUrl);
    
    chatSocket.onopen = function(e) {
        console.log('WebSocket connected successfully');
    };
    
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log('WebSocket message received:', data);
        
        if (data.type === 'chat_message') {
            appendMessage(data.message);
        } else if (data.type === 'message_sent') {
            // Message sent confirmation - update UI if needed
            console.log('Message sent successfully');
        } else if (data.type === 'error') {
            console.error('WebSocket error:', data.message);
            showError(data.message);
        } else if (data.type === 'pong') {
            console.log('Pong received - connection alive');
        }
    };
    
    chatSocket.onclose = function(e) {
        console.log('WebSocket disconnected:', e.code);
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
            if (conversationId) {
                initializeWebSocket(conversationId);
            }
        }, 3000);
    };
    
    chatSocket.onerror = function(e) {
        console.error('WebSocket error occurred:', e);
    };
    
    // Send ping every 30 seconds to keep connection alive
    setInterval(() => {
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({'type': 'ping'}));
        }
    }, 30000);
}

// Send message function
function sendMessage(content) {
    if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) {
        console.error('WebSocket not connected');
        showError('Connection lost. Trying to reconnect...');
        return;
    }
    
    const messageData = {
        type: 'chat_message',
        content: content,
        conversation_id: conversationId,
        timestamp: new Date().toISOString()
    };
    
    console.log('Sending message:', messageData);
    chatSocket.send(JSON.stringify(messageData));
}

// Append message to chat UI
function appendMessage(message) {
    const messagesContainer = document.getElementById('messages-container');
    if (!messagesContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${message.sender_id === getCurrentUserId() ? 'own-message' : 'other-message'}`;
    messageElement.innerHTML = `
        <div class="message-content">
            <p>${message.emoji_content || message.content}</p>
            <small>${new Date(message.timestamp).toLocaleTimeString()}</small>
        </div>
    `;
    
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show error message
function showError(message) {
    // You can customize this to match your UI
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    
    const container = document.querySelector('.messages-container') || document.body;
    container.insertBefore(errorDiv, container.firstChild);
    
    // Remove error after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

// Get current user ID (you need to implement this based on your template)
function getCurrentUserId() {
    // This should return the current user's ID
    // You can get it from a hidden input or data attribute in your template
    return window.currentUserId || null;
}

// Friend request functions
function acceptFriendRequest(requestId) {
    if (!requestId) {
        showError('Friend request ID is missing');
        return;
    }
    
    fetch('/chat/api/friend-request/accept/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            friend_request_id: requestId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Friend request accepted successfully!');
            // Refresh the page or update the UI
            location.reload();
        } else {
            showError(data.message || 'Failed to accept friend request');
        }
    })
    .catch(error => {
        console.error('Error accepting friend request:', error);
        showError('Failed to accept friend request');
    });
}

function declineFriendRequest(requestId) {
    if (!requestId) {
        showError('Friend request ID is missing');
        return;
    }
    
    fetch('/chat/api/friend-request/decline/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            friend_request_id: requestId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Friend request declined');
            // Refresh the page or update the UI
            location.reload();
        } else {
            showError(data.message || 'Failed to decline friend request');
        }
    })
    .catch(error => {
        console.error('Error declining friend request:', error);
        showError('Failed to decline friend request');
    });
}

// Get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

// Show success message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success';
    successDiv.textContent = message;
    
    const container = document.querySelector('.messages-container') || document.body;
    container.insertBefore(successDiv, container.firstChild);
    
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 3000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize WebSocket if conversation ID is available
    const convId = window.conversationId || document.querySelector('[data-conversation-id]')?.dataset.conversationId;
    if (convId) {
        initializeWebSocket(convId);
    }
    
    // Handle message form submission
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    
    if (messageForm && messageInput) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const content = messageInput.value.trim();
            if (content) {
                sendMessage(content);
                messageInput.value = '';
            }
        });
    }
});