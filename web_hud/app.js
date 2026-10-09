// ==========================================================================
// MAYA AI COCKPIT HUD CONTROLLER - FULL WEBSOCKET & VOICE INTEGRATION
// Connects to local Python server for real-time Windows control & mic
// ==========================================================================

const canvas = document.getElementById('audioCanvas');
const ctx = canvas.getContext('2d');
let animationFrameId;
let currentStatus = 'IDLE'; // IDLE, LISTENING, THINKING, SPEAKING

function resizeCanvas() {
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = canvas.parentElement.clientHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Organic Waveform Visualizer
let wavePhase = 0;
function drawWave() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;

  let baseColor = '#00E5FF';
  let amplitude = 14;
  let frequency = 0.02;
  let speed = 0.04;

  if (currentStatus === 'LISTENING') {
    baseColor = '#00E5FF';
    amplitude = 36;
    speed = 0.09;
  } else if (currentStatus === 'THINKING') {
    baseColor = '#F59E0B';
    amplitude = 20;
    speed = 0.12;
  } else if (currentStatus === 'SPEAKING') {
    baseColor = '#10B981';
    amplitude = 42;
    speed = 0.08;
  }

  // Draw Glow Circle Core
  ctx.save();
  ctx.beginPath();
  ctx.arc(cx, cy, 38, 0, Math.PI * 2);
  const glowGrad = ctx.createRadialGradient(cx, cy, 10, cx, cy, 60);
  glowGrad.addColorStop(0, baseColor);
  glowGrad.addColorStop(1, 'transparent');
  ctx.fillStyle = glowGrad;
  ctx.globalAlpha = 0.35;
  ctx.fill();
  ctx.restore();

  // Draw Oscillating Kinetic Waves
  ctx.save();
  ctx.lineWidth = 2.5;
  ctx.strokeStyle = baseColor;
  ctx.beginPath();

  for (let x = 0; x < canvas.width; x += 4) {
    const distFromCenter = Math.abs(x - cx) / (canvas.width / 2);
    const envelope = Math.max(0, 1 - distFromCenter);
    const y = cy + Math.sin(x * frequency + wavePhase) * amplitude * envelope;
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  // Second harmonic wave
  ctx.beginPath();
  ctx.lineWidth = 1.2;
  ctx.globalAlpha = 0.45;
  for (let x = 0; x < canvas.width; x += 4) {
    const distFromCenter = Math.abs(x - cx) / (canvas.width / 2);
    const envelope = Math.max(0, 1 - distFromCenter);
    const y = cy + Math.cos(x * (frequency * 1.5) - wavePhase * 1.2) * (amplitude * 0.7) * envelope;
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.restore();

  wavePhase += speed;
  animationFrameId = requestAnimationFrame(drawWave);
}
drawWave();

function setStatus(status, text) {
  currentStatus = status;
  const caption = document.getElementById('stageStatusCaption');
  const dot = document.getElementById('statusDot');
  const label = document.getElementById('statusLabel');

  if (caption) caption.innerText = text || `STATUS // ${status}`;
  if (label) label.innerText = status;

  if (dot) {
    if (status === 'IDLE') dot.style.background = '#00E5FF';
    else if (status === 'LISTENING') dot.style.background = '#00E5FF';
    else if (status === 'THINKING') dot.style.background = '#F59E0B';
    else if (status === 'SPEAKING') dot.style.background = '#10B981';
  }
}

function appendMessage(sender, text) {
  const feed = document.getElementById('transcriptFeed');
  if (!feed) return;

  const bubble = document.createElement('div');
  bubble.className = `message-bubble message-${sender.toLowerCase()}`;
  
  const meta = document.createElement('div');
  meta.className = 'message-meta';
  meta.innerText = `${sender.toUpperCase()} • ${new Date().toLocaleTimeString()}`;

  const content = document.createElement('div');
  content.innerText = text;

  bubble.appendChild(meta);
  bubble.appendChild(content);
  feed.appendChild(bubble);
  feed.scrollTop = feed.scrollHeight;
}

// ==========================================================================
// REAL-TIME WEBSOCKET BRIDGE TO PYTHON BACKEND
// ==========================================================================
let ws = null;
let reconnectTimer = null;

function connectWebSocket() {
  const host = window.location.host || '127.0.0.1:8000';
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${host}/ws`;

  console.log(`Connecting to WebSocket: ${wsUrl}`);
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('✅ WebSocket Connected to Maya AI Backend');
    setStatus('IDLE', 'CONNECTED // STANDBY FOR COMMANDS');
    const label = document.getElementById('statusLabel');
    if (label) label.innerText = 'SYSTEM ONLINE (WS CONNECTED)';
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);

      if (msg.type === 'telemetry') {
        updateTelemetry(msg.data);
      } else if (msg.type === 'status') {
        setStatus(msg.status, msg.caption);
      } else if (msg.type === 'transcript') {
        appendMessage(msg.sender, msg.text);
      }
    } catch (e) {
      console.error('Error parsing WS message:', e);
    }
  };

  ws.onclose = () => {
    console.warn('WebSocket Disconnected. Retrying in 2 seconds...');
    setStatus('IDLE', 'OFFLINE // RECONNECTING BACKEND...');
    const label = document.getElementById('statusLabel');
    if (label) label.innerText = 'DISCONNECTED (RETRYING)';
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(connectWebSocket, 2000);
  };

  ws.onerror = (err) => {
    console.error('WebSocket Error:', err);
  };
}

connectWebSocket();

function sendWS(payload) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(payload));
  } else {
    console.warn('WebSocket is not open, falling back to REST API');
    if (payload.type === 'command') {
      fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: payload.text })
      }).then(r => r.json()).then(res => {
        appendMessage('User', payload.text);
        appendMessage('Maya', res.response);
      }).catch(err => {
        appendMessage('System', 'Cannot connect to Maya backend. Please ensure server.py is running.');
      });
    }
  }
}

function updateTelemetry(data) {
  if (!data) return;
  if (data.cpu_percent !== undefined) {
    const cpuEl = document.getElementById('cpuValue');
    const cpuProg = document.getElementById('cpuProgress');
    if (cpuEl) cpuEl.innerText = `${data.cpu_percent}%`;
    if (cpuProg) cpuProg.style.width = `${Math.min(100, data.cpu_percent)}%`;
  }
  if (data.ram_percent !== undefined) {
    const ramEl = document.getElementById('ramValue');
    const ramProg = document.getElementById('ramProgress');
    if (ramEl) ramEl.innerText = `${data.ram_percent}%`;
    if (ramProg) ramProg.style.width = `${Math.min(100, data.ram_percent)}%`;
  }
  if (data.os) {
    const osEl = document.getElementById('osBadge');
    if (osEl) osEl.innerText = data.os.toUpperCase();
  }
}

// User Command Input Dispatcher
function submitCommand() {
  const input = document.getElementById('cmdInput');
  const text = input.value.trim();
  if (!text) return;

  sendWS({ type: 'command', text: text });
  input.value = '';
}

document.getElementById('cmdInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') submitCommand();
});

// Quick Action Card Dispatcher
function triggerQuickAction(commandText) {
  sendWS({ type: 'command', text: commandText });
}

// Persona Selector Dispatcher
function switchPersona(selectElement) {
  const personaKey = selectElement.value;
  sendWS({ type: 'persona', persona: personaKey });
}

// ==========================================================================
// BROWSER VOICE RECOGNITION (HTML5 Web Speech API)
// Gives instant voice control right from the web browser!
// ==========================================================================
let recognition = null;
let isBrowserListening = false;

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn('Web Speech API is not supported in this browser.');
    return null;
  }

  const rec = new SpeechRecognition();
  rec.continuous = false;
  rec.interimResults = false;
  rec.lang = 'en-US'; // Can also support 'vi-VN'

  rec.onstart = () => {
    isBrowserListening = true;
    setStatus('LISTENING', 'LISTENING TO YOUR VOICE...');
    const btn = document.getElementById('micBtn');
    if (btn) btn.style.borderColor = '#00E5FF';
  };

  rec.onresult = (event) => {
    const speechResult = event.results[0][0].transcript;
    console.log('Recognized speech:', speechResult);
    sendWS({ type: 'command', text: speechResult });
  };

  rec.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    isBrowserListening = false;
    setStatus('IDLE', 'STANDBY // READY');
  };

  rec.onend = () => {
    isBrowserListening = false;
    const btn = document.getElementById('micBtn');
    if (btn) btn.style.borderColor = 'rgba(0, 229, 255, 0.25)';
  };

  return rec;
}

recognition = initSpeechRecognition();

function toggleBrowserSpeech() {
  if (!recognition) {
    alert('Web Speech Recognition is not supported in this browser. Please use Google Chrome or Edge, or use native microphone with wake word "Maya"!');
    return;
  }

  if (isBrowserListening) {
    recognition.stop();
  } else {
    try {
      recognition.start();
    } catch (e) {
      console.warn('Recognition already started:', e);
    }
  }
}
