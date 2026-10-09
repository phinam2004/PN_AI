// ==========================================================================
// MAYA AI COCKPIT HUD CONTROLLER
// Handles real-time audio visualization, mock/live telemetry, and commands
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
  let amplitude = 12;
  let frequency = 0.02;
  let speed = 0.04;

  if (currentStatus === 'LISTENING') {
    baseColor = '#00E5FF';
    amplitude = 32;
    speed = 0.08;
  } else if (currentStatus === 'THINKING') {
    baseColor = '#F59E0B';
    amplitude = 18;
    speed = 0.12;
  } else if (currentStatus === 'SPEAKING') {
    baseColor = '#10B981';
    amplitude = 40;
    speed = 0.07;
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

  caption.innerText = text || `STATUS // ${status}`;
  label.innerText = status;

  if (status === 'IDLE') dot.style.background = '#00E5FF';
  else if (status === 'LISTENING') dot.style.background = '#00E5FF';
  else if (status === 'THINKING') dot.style.background = '#F59E0B';
  else if (status === 'SPEAKING') dot.style.background = '#10B981';
}

function appendMessage(sender, text) {
  const feed = document.getElementById('transcriptFeed');
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

// User Command Input Dispatcher
function submitCommand() {
  const input = document.getElementById('cmdInput');
  const text = input.value.trim();
  if (!text) return;

  appendMessage('User', text);
  input.value = '';

  setStatus('THINKING', 'MAYA IS THINKING...');

  // Mock processing / trigger backend
  setTimeout(() => {
    setStatus('SPEAKING', 'EXECUTING ACTION...');
    let reply = `Command '${text}' executed successfully.`;
    if (text.toLowerCase().includes('who are you')) {
      reply = "I am Maya, your personal AI assistant. Upgraded with cross-platform intelligence, advanced system automation, and lightning-fast voice execution.";
    } else if (text.toLowerCase().includes('battery')) {
      reply = "Battery is at 88%, currently connected to AC power.";
    } else if (text.toLowerCase().includes('focus')) {
      reply = "Focus Mode initiated: VS Code launched and ambient stream active.";
    }
    appendMessage('Maya', reply);

    setTimeout(() => {
      setStatus('IDLE', 'STANDBY // READY FOR WAKE WORD');
    }, 2500);
  }, 900);
}

document.getElementById('cmdInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') submitCommand();
});

// Telemetry Polling Simulator (real values populated when connected to backend)
setInterval(() => {
  const cpuVal = (Math.random() * 8 + 12).toFixed(1);
  const ramVal = 42;
  document.getElementById('cpuValue').innerText = `${cpuVal}%`;
  document.getElementById('cpuProgress').style.width = `${cpuVal}%`;
}, 2500);
