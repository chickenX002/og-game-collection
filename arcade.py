#!/usr/bin/env python3
"""
 ██████╗  ██████╗     ██████╗ █████╗ ██████╗ ██╗███╗   ██╗███████╗████████╗
██╔═══██╗██╔════╝    ██╔════╝██╔══██╗██╔══██╗██║████╗  ██║██╔════╝╚══██╔══╝
██║   ██║██║  ███╗   ██║     ███████║██████╔╝██║██╔██╗ ██║█████╗     ██║   
██║   ██║██║   ██║   ██║     ██╔══██║██╔══██╗██║██║╚██╗██║██╔══╝     ██║   
╚██████╔╝╚██████╔╝   ╚██████╗██║  ██║██████╔╝██║██║ ╚████║███████╗   ██║   
 ╚═════╝  ╚═════╝     ╚═════╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝  
Classic Arcade Collection — Snake, Pong, Tetris, Breakout, Flappy Bird
Run: python arcade.py  →  open http://localhost:5000
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OG ARCADE</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323:wght@400&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0f;
    --panel: #0f0f1a;
    --border: #1a1a2e;
    --neon-green: #39ff14;
    --neon-blue: #00f0ff;
    --neon-pink: #ff006e;
    --neon-yellow: #ffe600;
    --neon-orange: #ff6b00;
    --text: #e0e0ff;
    --dim: #4a4a6a;
    --scanline: rgba(0,0,0,0.15);
    --glow-green: 0 0 8px #39ff14, 0 0 20px #39ff14aa;
    --glow-blue: 0 0 8px #00f0ff, 0 0 20px #00f0ffaa;
    --glow-pink: 0 0 8px #ff006e, 0 0 20px #ff006eaa;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Press Start 2P', monospace;
    min-height: 100vh;
    overflow-x: hidden;
  }
  body::before {
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(0deg, var(--scanline) 0px, var(--scanline) 1px, transparent 1px, transparent 3px);
    pointer-events: none; z-index: 9999;
  }

  /* ── HEADER ── */
  header {
    text-align: center;
    padding: 2rem 1rem 1rem;
    border-bottom: 2px solid var(--border);
    position: relative;
  }
  .logo {
    font-size: clamp(1.4rem, 4vw, 2.6rem);
    color: var(--neon-green);
    text-shadow: var(--glow-green);
    letter-spacing: 4px;
    animation: flicker 4s infinite;
  }
  .logo span { color: var(--neon-pink); text-shadow: var(--glow-pink); }
  .tagline { font-size: 0.5rem; color: var(--dim); margin-top: 0.6rem; letter-spacing: 3px; }
  .insert-coin {
    font-size: 0.55rem;
    color: var(--neon-yellow);
    margin-top: 0.8rem;
    animation: blink 1.2s step-end infinite;
  }

  /* ── GAME SELECTOR ── */
  .game-select {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.6rem;
    padding: 1.2rem 1rem;
    border-bottom: 2px solid var(--border);
  }
  .game-btn {
    font-family: 'Press Start 2P', monospace;
    font-size: 0.5rem;
    padding: 0.6rem 1rem;
    border: 2px solid var(--dim);
    background: transparent;
    color: var(--dim);
    cursor: pointer;
    transition: all 0.15s;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .game-btn:hover, .game-btn.active {
    border-color: var(--neon-green);
    color: var(--neon-green);
    box-shadow: var(--glow-green), inset 0 0 12px #39ff1420;
    background: #39ff1408;
  }
  .game-btn.active { background: #39ff1415; }

  /* ── ARCADE CABINET ── */
  .arcade-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem 1rem 2rem;
    gap: 1rem;
  }
  .cabinet {
    border: 3px solid var(--neon-blue);
    box-shadow: var(--glow-blue), inset 0 0 30px #00f0ff08;
    background: var(--panel);
    padding: 6px;
    position: relative;
  }
  .cabinet::before {
    content: attr(data-game);
    position: absolute;
    top: -1.4rem; left: 0; right: 0;
    text-align: center;
    font-size: 0.45rem;
    color: var(--neon-blue);
    letter-spacing: 3px;
  }
  canvas { display: block; image-rendering: pixelated; }

  /* ── HUD ── */
  .hud {
    display: flex;
    gap: 2rem;
    font-size: 0.45rem;
    color: var(--dim);
    justify-content: center;
    flex-wrap: wrap;
  }
  .hud span { color: var(--neon-green); }
  .hud b { color: var(--text); }

  /* ── CONTROLS ── */
  .controls-panel {
    font-family: 'VT323', monospace;
    font-size: 1rem;
    color: var(--dim);
    text-align: center;
    max-width: 480px;
    line-height: 1.6;
    letter-spacing: 1px;
  }
  .controls-panel em { color: var(--neon-yellow); font-style: normal; }

  /* ── MOBILE D-PAD ── */
  .dpad-wrap {
    display: none;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    margin-top: 0.5rem;
  }
  @media (pointer: coarse) { .dpad-wrap { display: flex; } }
  .dpad-row { display: flex; gap: 4px; }
  .dpad-btn {
    width: 44px; height: 44px;
    font-size: 1.2rem;
    background: var(--panel);
    border: 2px solid var(--dim);
    color: var(--text);
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    user-select: none; -webkit-user-select: none;
    transition: background 0.1s;
    border-radius: 4px;
  }
  .dpad-btn:active { background: var(--neon-green); color: var(--bg); border-color: var(--neon-green); }

  /* ── OVERLAY ── */
  .overlay {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: #0a0a0fcc;
    gap: 1rem;
    backdrop-filter: blur(2px);
    z-index: 10;
  }
  .overlay h2 { font-size: 1rem; color: var(--neon-pink); text-shadow: var(--glow-pink); }
  .overlay p { font-size: 0.45rem; color: var(--dim); }
  .overlay .score-disp { font-size: 1.5rem; color: var(--neon-green); font-family: 'VT323'; }
  .start-btn {
    font-family: 'Press Start 2P', monospace;
    font-size: 0.5rem;
    padding: 0.7rem 1.4rem;
    background: transparent;
    border: 2px solid var(--neon-green);
    color: var(--neon-green);
    cursor: pointer;
    box-shadow: var(--glow-green);
    animation: blink 1s step-end infinite;
    letter-spacing: 2px;
  }
  .start-btn:hover { background: #39ff1420; animation: none; }

  @keyframes blink { 50% { opacity: 0; } }
  @keyframes flicker {
    0%,19%,21%,23%,25%,54%,56%,100% { opacity: 1; }
    20%,22%,24%,55% { opacity: 0.6; }
  }

  /* ── SCOREBOARD ── */
  .scoreboard {
    font-family: 'VT323', monospace;
    font-size: 1.1rem;
    border: 2px solid var(--border);
    padding: 1rem 2rem;
    min-width: 280px;
    text-align: center;
  }
  .scoreboard h3 {
    font-family: 'Press Start 2P', monospace;
    font-size: 0.45rem;
    color: var(--neon-yellow);
    margin-bottom: 0.6rem;
    letter-spacing: 2px;
  }
  .score-row {
    display: flex; justify-content: space-between;
    color: var(--dim); padding: 2px 0;
  }
  .score-row.best { color: var(--neon-green); }
</style>
</head>
<body>

<header>
  <div class="logo">OG <span>ARCADE</span></div>
  <div class="tagline">CLASSIC GAMES COLLECTION — ALL ORIGINALS</div>
  <div class="insert-coin">▶ INSERT COIN ◀</div>
</header>

<div class="game-select">
  <button class="game-btn active" onclick="switchGame('snake')">🐍 SNAKE</button>
  <button class="game-btn" onclick="switchGame('pong')">🏓 PONG</button>
  <button class="game-btn" onclick="switchGame('tetris')">🧱 TETRIS</button>
  <button class="game-btn" onclick="switchGame('breakout')">🧱 BREAKOUT</button>
  <button class="game-btn" onclick="switchGame('flappy')">🐦 FLAPPY</button>
</div>

<div class="arcade-wrap">
  <div class="cabinet" id="cabinet" data-game="SNAKE">
    <canvas id="gameCanvas" width="400" height="400"></canvas>
    <div class="overlay" id="overlay">
      <h2 id="overlayTitle">SNAKE</h2>
      <div class="score-disp" id="overlayScore"></div>
      <p id="overlayMsg">USE ARROW KEYS OR WASD</p>
      <button class="start-btn" id="startBtn" onclick="startGame()">PRESS START</button>
    </div>
  </div>

  <div class="hud">
    <div>SCORE <b id="scoreDisp">0</b></div>
    <div>BEST <b id="bestDisp">0</b></div>
    <div>LEVEL <b id="levelDisp">1</b></div>
  </div>

  <div class="controls-panel" id="controlsPanel">
    CONTROLS: <em>ARROWS / WASD</em> — MOVE &nbsp;|&nbsp; <em>P</em> — PAUSE
  </div>

  <!-- Mobile D-pad -->
  <div class="dpad-wrap" id="dpad">
    <div class="dpad-row"><button class="dpad-btn" id="dUp">▲</button></div>
    <div class="dpad-row">
      <button class="dpad-btn" id="dLeft">◀</button>
      <button class="dpad-btn" id="dDown">▼</button>
      <button class="dpad-btn" id="dRight">▶</button>
    </div>
  </div>

  <div class="scoreboard">
    <h3>— HIGH SCORES —</h3>
    <div id="scoreboardList"></div>
  </div>
</div>

<script>
// ═══════════════════════════════════════════════════════
//  ARCADE ENGINE
// ═══════════════════════════════════════════════════════
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('overlay');
const overlayTitle = document.getElementById('overlayTitle');
const overlayScore = document.getElementById('overlayScore');
const overlayMsg = document.getElementById('overlayMsg');
const scoreDisp = document.getElementById('scoreDisp');
const bestDisp = document.getElementById('bestDisp');
const levelDisp = document.getElementById('levelDisp');
const controlsPanel = document.getElementById('controlsPanel');

let currentGame = 'snake';
let gameLoop = null;
let score = 0;
let paused = false;
let gameRunning = false;

const bests = { snake: 0, pong: 0, tetris: 0, breakout: 0, flappy: 0 };

const COLORS = {
  bg: '#0a0a0f', panel: '#0f0f1a',
  green: '#39ff14', blue: '#00f0ff',
  pink: '#ff006e', yellow: '#ffe600',
  orange: '#ff6b00', dim: '#2a2a3a',
  text: '#e0e0ff', white: '#ffffff'
};

function setScore(s) {
  score = s;
  scoreDisp.textContent = s;
  if (s > bests[currentGame]) {
    bests[currentGame] = s;
    bestDisp.textContent = s;
    updateScoreboard();
  }
}
function setLevel(l) { levelDisp.textContent = l; }

function showOverlay(title, msg, scoreVal = '') {
  overlayTitle.textContent = title;
  overlayMsg.textContent = msg;
  overlayScore.textContent = scoreVal;
  document.getElementById('startBtn').textContent = scoreVal ? 'PLAY AGAIN' : 'PRESS START';
  overlay.style.display = 'flex';
  gameRunning = false;
}

function hideOverlay() {
  overlay.style.display = 'none';
  gameRunning = true;
}

function stopLoop() {
  if (gameLoop) { clearInterval(gameLoop); gameLoop = null; }
}

function switchGame(game) {
  stopLoop();
  currentGame = game;
  score = 0; paused = false;
  setScore(0); setLevel(1);
  bestDisp.textContent = bests[game];
  document.querySelectorAll('.game-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('cabinet').dataset.game = game.toUpperCase();
  // controls hints
  const hints = {
    snake:   'CONTROLS: ARROWS / WASD — MOVE &nbsp;|&nbsp; P — PAUSE',
    pong:    'CONTROLS: W/S — PLAYER 1 &nbsp;|&nbsp; ↑/↓ — PLAYER 2 &nbsp;|&nbsp; P — PAUSE',
    tetris:  'CONTROLS: ARROWS — MOVE/ROTATE &nbsp;|&nbsp; SPACE — DROP &nbsp;|&nbsp; P — PAUSE',
    breakout:'CONTROLS: ← → / A D — PADDLE &nbsp;|&nbsp; SPACE — LAUNCH &nbsp;|&nbsp; P — PAUSE',
    flappy:  'CONTROLS: SPACE / CLICK / TAP — FLAP &nbsp;|&nbsp; P — PAUSE'
  };
  controlsPanel.innerHTML = hints[game];
  const titles = { snake:'SNAKE', pong:'PONG', tetris:'TETRIS', breakout:'BREAKOUT', flappy:'FLAPPY BIRD' };
  showOverlay(titles[game], hints[game].replace(/&nbsp;/g,' ').replace(/<[^>]+>/g,''), '');
  clearCanvas();
  initGame();
}

function clearCanvas() {
  ctx.fillStyle = COLORS.bg;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function startGame() {
  stopLoop();
  score = 0; setScore(0); setLevel(1);
  paused = false;
  hideOverlay();
  clearCanvas();
  switch (currentGame) {
    case 'snake':    startSnake();    break;
    case 'pong':     startPong();     break;
    case 'tetris':   startTetris();   break;
    case 'breakout': startBreakout(); break;
    case 'flappy':   startFlappy();   break;
  }
}

function initGame() {
  switch (currentGame) {
    case 'snake':    drawSnakePreview();    break;
    case 'pong':     drawPongPreview();     break;
    case 'tetris':   drawTetrisPreview();   break;
    case 'breakout': drawBreakoutPreview(); break;
    case 'flappy':   drawFlappyPreview();   break;
  }
}

// ═══════════════════════════════════════════════════════
//  SNAKE
// ═══════════════════════════════════════════════════════
let snake, snakeDir, snakeNext, food, snakeSpeed;
const SZ = 20; // cell size

function drawSnakePreview() {
  clearCanvas();
  ctx.strokeStyle = COLORS.green + '22';
  for (let x = 0; x < canvas.width; x += SZ)
    ctx.strokeRect(x, 0, SZ, canvas.height);
}

function startSnake() {
  snake = [{x:10,y:10},{x:9,y:10},{x:8,y:10}];
  snakeDir = {x:1,y:0}; snakeNext = {x:1,y:0};
  spawnFood();
  snakeSpeed = 120;
  gameLoop = setInterval(tickSnake, snakeSpeed);
}

function spawnFood() {
  const cols = canvas.width/SZ, rows = canvas.height/SZ;
  let pos;
  do { pos = {x:Math.floor(Math.random()*cols), y:Math.floor(Math.random()*rows)}; }
  while (snake.some(s=>s.x===pos.x&&s.y===pos.y));
  food = pos;
}

function tickSnake() {
  if (paused) return;
  snakeDir = {...snakeNext};
  const head = {x: snake[0].x + snakeDir.x, y: snake[0].y + snakeDir.y};
  const cols = canvas.width/SZ, rows = canvas.height/SZ;
  if (head.x < 0||head.x >= cols||head.y < 0||head.y >= rows||
      snake.some(s=>s.x===head.x&&s.y===head.y)) {
    stopLoop();
    showOverlay('GAME OVER', 'SNAKE', 'SCORE: ' + score);
    return;
  }
  snake.unshift(head);
  if (head.x === food.x && head.y === food.y) {
    setScore(score + 10);
    const lvl = Math.floor(score/50)+1; setLevel(lvl);
    snakeSpeed = Math.max(60, 120 - (lvl-1)*8);
    clearInterval(gameLoop);
    gameLoop = setInterval(tickSnake, snakeSpeed);
    spawnFood();
  } else snake.pop();
  drawSnake();
}

function drawSnake() {
  clearCanvas();
  // grid
  ctx.strokeStyle = COLORS.dim + '55';
  ctx.lineWidth = 0.5;
  for (let x = 0; x < canvas.width; x += SZ) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,canvas.height); ctx.stroke(); }
  for (let y = 0; y < canvas.height; y += SZ) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke(); }
  // food
  ctx.fillStyle = COLORS.pink;
  ctx.shadowColor = COLORS.pink; ctx.shadowBlur = 12;
  ctx.fillRect(food.x*SZ+2, food.y*SZ+2, SZ-4, SZ-4);
  ctx.shadowBlur = 0;
  // snake
  snake.forEach((seg, i) => {
    const t = i / snake.length;
    ctx.fillStyle = i===0 ? COLORS.green : `hsl(${120-t*40},100%,${50-t*20}%)`;
    ctx.shadowColor = COLORS.green; ctx.shadowBlur = i===0?10:0;
    ctx.fillRect(seg.x*SZ+1, seg.y*SZ+1, SZ-2, SZ-2);
  });
  ctx.shadowBlur = 0;
}

// ═══════════════════════════════════════════════════════
//  PONG
// ═══════════════════════════════════════════════════════
let pong;

function drawPongPreview() {
  clearCanvas();
  ctx.setLineDash([10,10]);
  ctx.strokeStyle = COLORS.dim;
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(canvas.width/2,0); ctx.lineTo(canvas.width/2,canvas.height); ctx.stroke();
  ctx.setLineDash([]);
}

function startPong() {
  pong = {
    ball: {x:200,y:200,vx:3.5,vy:2.5},
    p1: {y:160, score:0}, p2: {y:160, score:0},
    ph: 80, pw: 10, keys: {}
  };
  gameLoop = setInterval(tickPong, 16);
}

function tickPong() {
  if (paused) return;
  const P = pong, W = canvas.width, H = canvas.height;
  if (P.keys['w']||P.keys['W']) P.p1.y = Math.max(0, P.p1.y - 5);
  if (P.keys['s']||P.keys['S']) P.p1.y = Math.min(H-P.ph, P.p1.y + 5);
  if (P.keys['ArrowUp'])   P.p2.y = Math.max(0, P.p2.y - 5);
  if (P.keys['ArrowDown']) P.p2.y = Math.min(H-P.ph, P.p2.y + 5);
  P.ball.x += P.ball.vx; P.ball.y += P.ball.vy;
  if (P.ball.y<=4||P.ball.y>=H-4) P.ball.vy *= -1;
  // p1 paddle
  if (P.ball.x<=P.pw+14 && P.ball.y>=P.p1.y && P.ball.y<=P.p1.y+P.ph) {
    P.ball.vx = Math.abs(P.ball.vx)*1.05;
    P.ball.vy += (P.ball.y-(P.p1.y+P.ph/2))*0.12;
  }
  // p2 paddle
  if (P.ball.x>=W-P.pw-14 && P.ball.y>=P.p2.y && P.ball.y<=P.p2.y+P.ph) {
    P.ball.vx = -Math.abs(P.ball.vx)*1.05;
    P.ball.vy += (P.ball.y-(P.p2.y+P.ph/2))*0.12;
  }
  P.ball.vx = Math.max(-8,Math.min(8,P.ball.vx));
  P.ball.vy = Math.max(-8,Math.min(8,P.ball.vy));
  if (P.ball.x<0) { P.p2.score++; resetBall(1); }
  if (P.ball.x>W) { P.p1.score++; resetBall(-1); }
  setScore(P.p1.score*10 + P.p2.score*5);
  if (P.p1.score>=7||P.p2.score>=7) {
    stopLoop();
    showOverlay('GAME OVER','PONG', (P.p1.score>P.p2.score?'P1':'P2')+' WINS!');
  }
  drawPong();
}

function resetBall(dir) {
  pong.ball = {x:200,y:200, vx:3.5*dir, vy:(Math.random()-0.5)*4};
}

function drawPong() {
  const P = pong, W = canvas.width, H = canvas.height;
  clearCanvas();
  // center line
  ctx.setLineDash([10,10]); ctx.strokeStyle = COLORS.dim; ctx.lineWidth=2;
  ctx.beginPath(); ctx.moveTo(W/2,0); ctx.lineTo(W/2,H); ctx.stroke(); ctx.setLineDash([]);
  // scores
  ctx.fillStyle = COLORS.dim; ctx.font = '2rem VT323, monospace';
  ctx.textAlign = 'center';
  ctx.fillText(P.p1.score, W/4, 40);
  ctx.fillText(P.p2.score, 3*W/4, 40);
  // paddles
  [[4, P.p1.y, COLORS.blue], [W-P.pw-4, P.p2.y, COLORS.pink]].forEach(([x,y,c])=>{
    ctx.fillStyle = c; ctx.shadowColor = c; ctx.shadowBlur = 12;
    ctx.fillRect(x, y, P.pw, P.ph); ctx.shadowBlur=0;
  });
  // ball
  ctx.fillStyle = COLORS.yellow; ctx.shadowColor = COLORS.yellow; ctx.shadowBlur = 16;
  ctx.fillRect(P.ball.x-5, P.ball.y-5, 10, 10); ctx.shadowBlur=0;
  ctx.textAlign='left';
}

// ═══════════════════════════════════════════════════════
//  TETRIS
// ═══════════════════════════════════════════════════════
const PIECES = [
  [[1,1,1,1]], [[1,1],[1,1]],
  [[0,1,0],[1,1,1]], [[1,0,0],[1,1,1]],
  [[0,0,1],[1,1,1]], [[1,1,0],[0,1,1]],
  [[0,1,1],[1,1,0]]
];
const PIECE_COLORS = [COLORS.blue,COLORS.yellow,COLORS.pink,COLORS.orange,COLORS.green,'#b400ff','#ff4400'];
const TC=20, TR=20, CW=canvas.width/TC, CH=canvas.height/TR;
let board, piece, pieceX, pieceY, pieceColor, tetrisTimer, tetrisLevel, tetrisLines;

function drawTetrisPreview() {
  clearCanvas();
  ctx.strokeStyle = COLORS.dim+'44'; ctx.lineWidth=0.5;
  for(let x=0;x<TC;x++) for(let y=0;y<TR;y++) ctx.strokeRect(x*CW,y*CH,CW,CH);
}

function startTetris() {
  board = Array.from({length:TR},()=>Array(TC).fill(0));
  tetrisLevel=1; tetrisLines=0; setLevel(1);
  spawnPiece(); drawTetris();
  tetrisTimer = setInterval(()=>{ if(!paused) dropPiece(); }, 600);
}

function spawnPiece() {
  const idx = Math.floor(Math.random()*PIECES.length);
  piece = PIECES[idx].map(r=>[...r]);
  pieceColor = PIECE_COLORS[idx];
  pieceX = Math.floor(TC/2)-Math.floor(piece[0].length/2);
  pieceY = 0;
  if (collides(piece,pieceX,pieceY)) {
    stopLoop();
    showOverlay('GAME OVER','TETRIS','SCORE: '+score);
  }
}

function collides(p,ox,oy) {
  for(let r=0;r<p.length;r++) for(let c=0;c<p[r].length;c++) {
    if(!p[r][c]) continue;
    const nx=ox+c, ny=oy+r;
    if(nx<0||nx>=TC||ny>=TR) return true;
    if(ny>=0&&board[ny][nx]) return true;
  }
  return false;
}

function dropPiece() {
  pieceY++;
  if(collides(piece,pieceX,pieceY)) {
    pieceY--;
    lockPiece();
  }
  drawTetris();
}

function lockPiece() {
  piece.forEach((r,ri)=>r.forEach((c,ci)=>{ if(c&&pieceY+ri>=0) board[pieceY+ri][pieceX+ci]=pieceColor; }));
  // clear lines
  let cleared=0;
  for(let r=TR-1;r>=0;r--) {
    if(board[r].every(c=>c)) { board.splice(r,1); board.unshift(Array(TC).fill(0)); cleared++; r++; }
  }
  if(cleared){
    const pts=[0,40,100,300,1200][cleared]*tetrisLevel;
    setScore(score+pts);
    tetrisLines+=cleared;
    tetrisLevel=Math.floor(tetrisLines/10)+1; setLevel(tetrisLevel);
    clearInterval(tetrisTimer);
    tetrisTimer=setInterval(()=>{ if(!paused) dropPiece(); }, Math.max(80,600-tetrisLevel*50));
  }
  spawnPiece();
}

function rotatePiece() {
  const rot = piece[0].map((_,i)=>piece.map(r=>r[i]).reverse());
  if(!collides(rot,pieceX,pieceY)) piece=rot;
}

function hardDrop() {
  while(!collides(piece,pieceX,pieceY+1)) pieceY++;
  dropPiece();
}

function drawTetris() {
  clearCanvas();
  // board
  board.forEach((row,r)=>row.forEach((col,c)=>{
    if(col){ ctx.fillStyle=col; ctx.shadowColor=col; ctx.shadowBlur=4; ctx.fillRect(c*CW+1,r*CH+1,CW-2,CH-2); ctx.shadowBlur=0; }
    else { ctx.strokeStyle=COLORS.dim+'33'; ctx.lineWidth=0.5; ctx.strokeRect(c*CW,r*CH,CW,CH); }
  }));
  // ghost
  let ghostY=pieceY;
  while(!collides(piece,pieceX,ghostY+1)) ghostY++;
  piece.forEach((r,ri)=>r.forEach((c,ci)=>{ if(c){ ctx.fillStyle=pieceColor+'30'; ctx.fillRect((pieceX+ci)*CW+1,(ghostY+ri)*CH+1,CW-2,CH-2); } }));
  // active piece
  piece.forEach((r,ri)=>r.forEach((c,ci)=>{ if(c&&pieceY+ri>=0){ ctx.fillStyle=pieceColor; ctx.shadowColor=pieceColor; ctx.shadowBlur=8; ctx.fillRect((pieceX+ci)*CW+1,(pieceY+ri)*CH+1,CW-2,CH-2); ctx.shadowBlur=0; } }));
}

// ═══════════════════════════════════════════════════════
//  BREAKOUT
// ═══════════════════════════════════════════════════════
let bo;

function drawBreakoutPreview() {
  clearCanvas();
  for(let r=0;r<5;r++) for(let c=0;c<8;c++) {
    const colors=[COLORS.pink,COLORS.orange,COLORS.yellow,COLORS.green,COLORS.blue];
    ctx.fillStyle=colors[r]+'66';
    ctx.fillRect(c*48+10,r*24+30,44,20);
  }
}

function startBreakout() {
  const bricks=[];
  const colors=[COLORS.pink,COLORS.orange,COLORS.yellow,COLORS.green,COLORS.blue];
  for(let r=0;r<5;r++) for(let c=0;c<8;c++)
    bricks.push({x:c*48+10,y:r*24+30,w:44,h:20,alive:true,color:colors[r],pts:(5-r)*10});
  bo={ bricks, paddle:{x:160,y:375,w:80,h:10}, ball:{x:200,y:350,vx:3,vy:-3}, launched:false, keys:{} };
  gameLoop = setInterval(()=>{ if(!paused) tickBreakout(); }, 16);
}

function tickBreakout() {
  const B=bo, W=canvas.width, H=canvas.height;
  if(B.keys['ArrowLeft']||B.keys['a']||B.keys['A']) B.paddle.x=Math.max(0,B.paddle.x-6);
  if(B.keys['ArrowRight']||B.keys['d']||B.keys['D']) B.paddle.x=Math.min(W-B.paddle.w,B.paddle.x+6);
  if(!B.launched){ B.ball.x=B.paddle.x+B.paddle.w/2; drawBreakout(); return; }
  B.ball.x+=B.ball.vx; B.ball.y+=B.ball.vy;
  if(B.ball.x<=4||B.ball.x>=W-4) B.ball.vx*=-1;
  if(B.ball.y<=4) B.ball.vy*=-1;
  if(B.ball.y>H){ stopLoop(); showOverlay('GAME OVER','BREAKOUT','SCORE: '+score); return; }
  // paddle
  if(B.ball.y>=B.paddle.y-4&&B.ball.y<=B.paddle.y+B.paddle.h&&B.ball.x>=B.paddle.x&&B.ball.x<=B.paddle.x+B.paddle.w){
    B.ball.vy=-Math.abs(B.ball.vy);
    B.ball.vx+=(B.ball.x-(B.paddle.x+B.paddle.w/2))*0.1;
  }
  // bricks
  B.bricks.forEach(br=>{ if(!br.alive) return;
    if(B.ball.x>=br.x&&B.ball.x<=br.x+br.w&&B.ball.y>=br.y&&B.ball.y<=br.y+br.h){
      br.alive=false; B.ball.vy*=-1; setScore(score+br.pts);
    }
  });
  if(B.bricks.every(b=>!b.alive)){ stopLoop(); showOverlay('YOU WIN!','BREAKOUT','SCORE: '+score); }
  drawBreakout();
}

function drawBreakout() {
  const B=bo;
  clearCanvas();
  B.bricks.forEach(br=>{ if(!br.alive) return;
    ctx.fillStyle=br.color; ctx.shadowColor=br.color; ctx.shadowBlur=6;
    ctx.fillRect(br.x,br.y,br.w,br.h); ctx.shadowBlur=0;
    ctx.strokeStyle='#00000044'; ctx.lineWidth=1; ctx.strokeRect(br.x,br.y,br.w,br.h);
  });
  ctx.fillStyle=COLORS.blue; ctx.shadowColor=COLORS.blue; ctx.shadowBlur=12;
  ctx.fillRect(B.paddle.x,B.paddle.y,B.paddle.w,B.paddle.h); ctx.shadowBlur=0;
  ctx.fillStyle=COLORS.white; ctx.shadowColor=COLORS.yellow; ctx.shadowBlur=16;
  ctx.beginPath(); ctx.arc(B.ball.x,B.ball.y,6,0,Math.PI*2); ctx.fill(); ctx.shadowBlur=0;
}

// ═══════════════════════════════════════════════════════
//  FLAPPY BIRD
// ═══════════════════════════════════════════════════════
let fb;

function drawFlappyPreview() {
  clearCanvas();
  ctx.fillStyle=COLORS.green+'44';
  ctx.fillRect(0,canvas.height-60,canvas.width,60);
  ctx.fillStyle=COLORS.yellow; ctx.shadowColor=COLORS.yellow; ctx.shadowBlur=12;
  ctx.beginPath(); ctx.arc(80,200,16,0,Math.PI*2); ctx.fill(); ctx.shadowBlur=0;
}

function startFlappy() {
  fb={ bird:{x:80,y:200,vy:0}, pipes:[], frameCount:0, gap:110, pipeW:40, started:false };
  gameLoop = setInterval(()=>{ if(!paused) tickFlappy(); }, 20);
}

function tickFlappy() {
  const F=fb, W=canvas.width, H=canvas.height;
  if(!F.started){ drawFlappy(); return; }
  F.bird.vy += 0.45;
  F.bird.y += F.bird.vy;
  if(F.bird.y<8||F.bird.y>H-8){ stopLoop(); showOverlay('GAME OVER','FLAPPY','SCORE: '+score); return; }
  F.frameCount++;
  if(F.frameCount%90===0){
    const topH=40+Math.random()*(H-F.gap-80);
    F.pipes.push({x:W,topH,passed:false});
  }
  F.pipes.forEach(p=>{ p.x-=2.5; });
  F.pipes = F.pipes.filter(p=>p.x>-F.pipeW);
  // score
  F.pipes.forEach(p=>{
    if(!p.passed&&p.x+F.pipeW<F.bird.x){ p.passed=true; setScore(score+1); setLevel(Math.floor(score/5)+1); }
    if(F.bird.x+14>p.x&&F.bird.x-14<p.x+F.pipeW&&(F.bird.y-14<p.topH||F.bird.y+14>p.topH+F.gap)){
      stopLoop(); showOverlay('GAME OVER','FLAPPY','SCORE: '+score);
    }
  });
  drawFlappy();
}

function flap() {
  if(!gameRunning) return;
  if(fb){ fb.bird.vy=-7; fb.started=true; }
}

function drawFlappy() {
  const F=fb, W=canvas.width, H=canvas.height;
  // sky gradient
  const sky=ctx.createLinearGradient(0,0,0,H);
  sky.addColorStop(0,'#0a0a1f'); sky.addColorStop(1,'#0a1a0a');
  ctx.fillStyle=sky; ctx.fillRect(0,0,W,H);
  // pipes
  F.pipes.forEach(p=>{
    ctx.fillStyle=COLORS.green; ctx.shadowColor=COLORS.green; ctx.shadowBlur=8;
    ctx.fillRect(p.x,0,F.pipeW,p.topH);
    ctx.fillRect(p.x,p.topH+F.gap,F.pipeW,H-p.topH-F.gap);
    ctx.shadowBlur=0;
    // pipe caps
    ctx.fillStyle='#00cc00';
    ctx.fillRect(p.x-4,p.topH-20,F.pipeW+8,20);
    ctx.fillRect(p.x-4,p.topH+F.gap,F.pipeW+8,20);
  });
  // ground
  ctx.fillStyle='#0a2a0a';
  ctx.fillRect(0,H-30,W,30);
  ctx.fillStyle=COLORS.green+'55';
  ctx.fillRect(0,H-30,W,4);
  // bird
  const tilt=Math.max(-0.4,Math.min(0.8,F.bird.vy*0.08));
  ctx.save(); ctx.translate(F.bird.x,F.bird.y); ctx.rotate(tilt);
  ctx.fillStyle=COLORS.yellow; ctx.shadowColor=COLORS.yellow; ctx.shadowBlur=14;
  ctx.beginPath(); ctx.ellipse(0,0,14,10,0,0,Math.PI*2); ctx.fill();
  ctx.shadowBlur=0;
  ctx.fillStyle=COLORS.orange;
  ctx.beginPath(); ctx.moveTo(10,-2); ctx.lineTo(18,0); ctx.lineTo(10,4); ctx.closePath(); ctx.fill();
  ctx.fillStyle='#fff'; ctx.beginPath(); ctx.arc(4,-3,4,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='#000'; ctx.beginPath(); ctx.arc(5,-3,2,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

// ═══════════════════════════════════════════════════════
//  INPUT HANDLING
// ═══════════════════════════════════════════════════════
document.addEventListener('keydown', e => {
  if(!gameRunning) return;
  // pong / breakout keys
  if(bo) bo.keys[e.key]=true;
  if(pong) pong.keys[e.key]=true;
  if(e.key==='p'||e.key==='P') {
    paused=!paused;
    if(paused){ ctx.fillStyle='#0a0a0fcc'; ctx.fillRect(0,0,canvas.width,canvas.height);
      ctx.fillStyle=COLORS.yellow; ctx.font='0.8rem "Press Start 2P"'; ctx.textAlign='center';
      ctx.fillText('PAUSED',canvas.width/2,canvas.height/2); ctx.textAlign='left'; }
    return;
  }
  if(currentGame==='snake'&&snakeDir) {
    const map={ArrowUp:{x:0,y:-1},ArrowDown:{x:0,y:1},ArrowLeft:{x:-1,y:0},ArrowRight:{x:1,y:0},
               w:{x:0,y:-1},s:{x:0,y:1},a:{x:-1,y:0},d:{x:1,y:0},
               W:{x:0,y:-1},S:{x:0,y:1},A:{x:-1,y:0},D:{x:1,y:0}};
    const d=map[e.key];
    if(d&&!(d.x===-snakeDir.x&&snakeDir.x!==0)&&!(d.y===-snakeDir.y&&snakeDir.y!==0)) snakeNext=d;
    e.preventDefault();
  }
  if(currentGame==='tetris') {
    if(e.key==='ArrowLeft') { if(!collides(piece,pieceX-1,pieceY)) pieceX--; drawTetris(); }
    if(e.key==='ArrowRight'){ if(!collides(piece,pieceX+1,pieceY)) pieceX++; drawTetris(); }
    if(e.key==='ArrowDown') dropPiece();
    if(e.key==='ArrowUp') { rotatePiece(); drawTetris(); }
    if(e.key===' ') hardDrop();
    if(['ArrowLeft','ArrowRight','ArrowDown','ArrowUp',' '].includes(e.key)) e.preventDefault();
  }
  if(currentGame==='breakout') {
    if(e.key===' ') { bo.launched=true; e.preventDefault(); }
  }
  if(currentGame==='flappy') {
    if(e.key===' ') { flap(); e.preventDefault(); }
  }
});

document.addEventListener('keyup', e => {
  if(bo) bo.keys[e.key]=false;
  if(pong) pong.keys[e.key]=false;
});

canvas.addEventListener('click', ()=>{ if(currentGame==='flappy') flap(); });
canvas.addEventListener('touchstart', e=>{ e.preventDefault(); if(currentGame==='flappy') flap(); },{passive:false});

// Mobile D-pad
function setupDpad() {
  const map = { dUp:'ArrowUp', dDown:'ArrowDown', dLeft:'ArrowLeft', dRight:'ArrowRight' };
  Object.entries(map).forEach(([id, key]) => {
    const btn = document.getElementById(id);
    const fire = () => { document.dispatchEvent(new KeyboardEvent('keydown',{key,bubbles:true})); };
    btn.addEventListener('touchstart', e=>{ e.preventDefault(); fire(); },{passive:false});
    btn.addEventListener('mousedown', fire);
  });
}
setupDpad();

// ═══════════════════════════════════════════════════════
//  SCOREBOARD
// ═══════════════════════════════════════════════════════
function updateScoreboard() {
  const list = document.getElementById('scoreboardList');
  const games = {snake:'🐍 SNAKE',pong:'🏓 PONG',tetris:'🧱 TETRIS',breakout:'🔴 BREAKOUT',flappy:'🐦 FLAPPY'};
  list.innerHTML = Object.entries(bests).map(([g,s])=>
    `<div class="score-row${g===currentGame?' best':''}">
      <span>${games[g]}</span><span>${s}</span>
    </div>`
  ).join('');
}
updateScoreboard();

// ── INIT ──
showOverlay('SNAKE', 'USE ARROW KEYS OR WASD', '');
drawSnakePreview();
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"  [{self.address_string()}] {format % args}")

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path == '/api/scores':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    PORT = 5000
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"""
  ██████╗  ██████╗      █████╗ ██████╗  ██████╗ █████╗ ██████╗ ███████╗
 ██╔═══██╗██╔════╝     ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝
 ██║   ██║██║  ███╗    ███████║██████╔╝██║     ███████║██║  ██║█████╗  
 ██║   ██║██║   ██║    ██╔══██║██╔══██╗██║     ██╔══██║██║  ██║██╔══╝  
 ╚██████╔╝╚██████╔╝    ██║  ██║██║  ██║╚██████╗██║  ██║██████╔╝███████╗
  ╚═════╝  ╚═════╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝

  🕹️  Server running at → http://localhost:{PORT}
  🐍  Snake  |  🏓 Pong  |  🧱 Tetris  |  🔴 Breakout  |  🐦 Flappy Bird
  Press CTRL+C to stop
    """)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  👾 Server stopped. Game over!")
        server.shutdown()
