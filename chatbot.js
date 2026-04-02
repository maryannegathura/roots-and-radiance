// Roots & Radiance Chatbot Widget
(function() {
  'use strict';

  // Brand colors
  const COLORS = {
    green: '#228B22',
    lightGreen: '#90EE90',
    brown: '#8B4513'
  };

  let sessionId = localStorage.getItem('chatSessionId');
  let isTyping = false;
  let currentInput = '';

  // Create elements
  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble';
  bubble.innerHTML = '💬';
  bubble.style.fontSize = '24px';
  bubble.style.display = 'flex';
  bubble.style.alignItems = 'center';
  bubble.style.justifyContent = 'center';

  const windowEl = document.createElement('div');
  windowEl.className = 'chat-window';
  windowEl.innerHTML = `
    <div class="chat-header">
      <span>Roots & Radiance — Hair Care Assistant</span>
      <button class="chat-close" onclick="window.chatWidget.toggle()">×</button>
    </div>
    <div class="quick-replies">
      <button class="quick-btn" data-reply="What are the benefits?">Benefits?</button>
      <button class="quick-btn" data-reply="How do I use it?">How to use?</button>
      <button class="quick-btn" data-reply="What's in it?">Ingredients?</button>
      <button class="quick-btn" data-reply="How do I order?">Order</button>
      <button class="quick-btn" data-reply="Contact support">Contact</button>
    </div>
    <div class="chat-messages" id="chatMessages"></div>
    <div class="typing-indicator" id="typingIndicator">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
    <div class="chat-input-area">
      <input type="text" class="chat-input" id="chatInput" placeholder="Type your message..." />
      <button class="send-btn" id="sendBtn">➤</button>
    </div>
  `;

  // Append to body
  document.body.appendChild(bubble);
  document.body.appendChild(windowEl);
  window.chatWidget = window.chatWidget || {};

  // Load CSS
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = '/chatbot.css';
  document.head.appendChild(link);

  // Init session
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('chatSessionId', sessionId);
  }

  const messagesEl = document.getElementById('chatMessages');
  const typingEl = document.getElementById('typingIndicator');
  const inputEl = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const quickBtns = windowEl.querySelectorAll('.quick-btn');

  // Event listeners
  bubble.onclick = () => chatWidget.toggle();
  window.chatWidget.toggle = () => {
    windowEl.style.display = windowEl.style.display === 'flex' ? 'none' : 'flex';
    if (windowEl.style.display === 'flex') loadHistory();
  };

  sendBtn.onclick = sendMessage;
  inputEl.onkeypress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  quickBtns.forEach(btn => {
    btn.onclick = () => {
      inputEl.value = btn.dataset.reply;
      sendMessage();
    };
  });

  function sendMessage() {
    const message = inputEl.value.trim();
    if (!message || isTyping) return;

    inputEl.value = '';
    addMessage('user', message);
    isTyping = true;
    typingEl.style.display = 'flex';
    sendBtn.disabled = true;

    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId })
    })
    .then(res => res.json())
    .then(data => {
      typingEl.style.display = 'none';
      isTyping = false;
      sendBtn.disabled = false;
      if (data.reply) addMessage('bot', data.reply);
      sessionId = data.session_id;
      localStorage.setItem('chatSessionId', sessionId);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    })
    .catch(err => {
      typingEl.style.display = 'none';
      isTyping = false;
      sendBtn.disabled = false;
      addMessage('bot', 'Sorry, something went wrong. Please try again.');
    });
  }

  function addMessage(sender, text) {
    const div = document.createElement('div');
    div.className = `message ${sender}-message`;
    div.innerHTML = `<div class="message-bubble">${text.replace(/\n/g, '<br>')}</div>`;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function loadHistory() {
    fetch(`/api/chat/history/${sessionId}`)
      .then(res => res.json())
      .then(data => {
        messagesEl.innerHTML = '';
        data.history.forEach(msg => addMessage(msg.sender, msg.message));
      })
      .catch(() => {});  // No history yet
  }

})();

