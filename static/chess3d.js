// 3D Chess Game using Three.js
const API_URL = window.location.origin;

// Three.js setup
let scene, camera, renderer, controls;
let boardGroup, piecesGroup;
let selectedPiece = null;
let selectedSquare = null;
let legalMoves = [];
let currentFen = '';
let moveHistory = [];
let selfPlayInterval = null;

// Colors
const LIGHT_SQUARE_COLOR = 0xf0d9b5;
const DARK_SQUARE_COLOR = 0xb58863;
const HIGHLIGHT_COLOR = 0x90ee90;
const SELECT_COLOR = 0xffff00;

// Initialize
init();
animate();
loadGamesList();
updateBoard();

function init() {
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    
    // Camera
    camera = new THREE.PerspectiveCamera(
        45,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(12, 12, 12);
    camera.lookAt(3.5, 0, 3.5);
    
    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('container').appendChild(renderer.domElement);
    
    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.left = -10;
    directionalLight.shadow.camera.right = 10;
    directionalLight.shadow.camera.top = 10;
    directionalLight.shadow.camera.bottom = -10;
    scene.add(directionalLight);
    
    // Create board
    createBoard();
    
    // Mouse controls
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    
    renderer.domElement.addEventListener('click', (event) => {
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(scene.children, true);
        
        if (intersects.length > 0) {
            handleClick(intersects[0]);
        }
    });
    
    // Window resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
    
    // Mouse rotation
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    
    renderer.domElement.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });
    
    renderer.domElement.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const deltaX = e.clientX - previousMousePosition.x;
            const deltaY = e.clientY - previousMousePosition.y;
            
            const rotationSpeed = 0.005;
            
            // Rotate camera around the board
            const radius = Math.sqrt(
                Math.pow(camera.position.x - 3.5, 2) +
                Math.pow(camera.position.z - 3.5, 2)
            );
            
            const currentAngle = Math.atan2(
                camera.position.z - 3.5,
                camera.position.x - 3.5
            );
            
            const newAngle = currentAngle - deltaX * rotationSpeed;
            
            camera.position.x = 3.5 + radius * Math.cos(newAngle);
            camera.position.z = 3.5 + radius * Math.sin(newAngle);
            camera.position.y = Math.max(5, camera.position.y - deltaY * 0.1);
            
            camera.lookAt(3.5, 0, 3.5);
            
            previousMousePosition = { x: e.clientX, y: e.clientY };
        }
    });
    
    renderer.domElement.addEventListener('mouseup', () => {
        isDragging = false;
    });
    
    // Zoom with mouse wheel
    renderer.domElement.addEventListener('wheel', (e) => {
        e.preventDefault();
        const zoomSpeed = 0.1;
        const direction = e.deltaY > 0 ? 1 : -1;
        
        const toCenter = new THREE.Vector3(3.5, 0, 3.5);
        const fromCamera = new THREE.Vector3().subVectors(camera.position, toCenter);
        
        fromCamera.multiplyScalar(1 + direction * zoomSpeed);
        camera.position.copy(toCenter.add(fromCamera));
        
        camera.lookAt(3.5, 0, 3.5);
    });
}

function createBoard() {
    boardGroup = new THREE.Group();
    
    // Create squares
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const isLight = (row + col) % 2 === 0;
            const geometry = new THREE.BoxGeometry(1, 0.2, 1);
            const material = new THREE.MeshStandardMaterial({
                color: isLight ? LIGHT_SQUARE_COLOR : DARK_SQUARE_COLOR
            });
            const square = new THREE.Mesh(geometry, material);
            square.position.set(col, -0.1, row);
            square.receiveShadow = true;
            square.userData = { type: 'square', row, col };
            boardGroup.add(square);
        }
    }
    
    // Board border
    const borderGeometry = new THREE.BoxGeometry(9, 0.5, 9);
    const borderMaterial = new THREE.MeshStandardMaterial({ color: 0x8b4513 });
    const border = new THREE.Mesh(borderGeometry, borderMaterial);
    border.position.set(3.5, -0.35, 3.5);
    border.receiveShadow = true;
    boardGroup.add(border);
    
    scene.add(boardGroup);
}

function createPiece(type, color, row, col) {
    const group = new THREE.Group();
    
    // Base
    const baseGeometry = new THREE.CylinderGeometry(0.3, 0.35, 0.1, 16);
    const material = new THREE.MeshStandardMaterial({
        color: color === 'white' ? 0xeeeeee : 0x333333
    });
    const base = new THREE.Mesh(baseGeometry, material);
    base.castShadow = true;
    group.add(base);
    
    // Body based on piece type
    let body;
    switch (type.toLowerCase()) {
        case 'p': // Pawn
            body = new THREE.Mesh(
                new THREE.SphereGeometry(0.2, 16, 16),
                material
            );
            body.position.y = 0.3;
            break;
        case 'n': // Knight
            body = new THREE.Mesh(
                new THREE.ConeGeometry(0.25, 0.6, 4),
                material
            );
            body.position.y = 0.35;
            body.rotation.y = Math.PI / 4;
            break;
        case 'b': // Bishop
            body = new THREE.Mesh(
                new THREE.ConeGeometry(0.2, 0.7, 16),
                material
            );
            body.position.y = 0.4;
            break;
        case 'r': // Rook
            body = new THREE.Mesh(
                new THREE.BoxGeometry(0.4, 0.6, 0.4),
                material
            );
            body.position.y = 0.35;
            break;
        case 'q': // Queen
            body = new THREE.Mesh(
                new THREE.ConeGeometry(0.25, 0.8, 8),
                material
            );
            body.position.y = 0.45;
            break;
        case 'k': // King
            body = new THREE.Mesh(
                new THREE.ConeGeometry(0.25, 0.9, 6),
                material
            );
            body.position.y = 0.5;
            const cross = new THREE.Mesh(
                new THREE.BoxGeometry(0.15, 0.3, 0.05),
                material
            );
            cross.position.y = 0.8;
            group.add(cross);
            break;
    }
    
    if (body) {
        body.castShadow = true;
        group.add(body);
    }
    
    group.position.set(col, 0, row);
    group.userData = { type: 'piece', pieceType: type, color, row, col };
    
    return group;
}

function updateBoard() {
    fetch(`${API_URL}/api/board`)
        .then(response => response.json())
        .then(data => {
            currentFen = data.fen;
            legalMoves = data.legal_moves;
            
            // Update turn display
            document.getElementById('turn').textContent = 
                data.turn.charAt(0).toUpperCase() + data.turn.slice(1);
            
            // Update game status
            if (data.is_game_over) {
                document.getElementById('gameStatus').textContent = 
                    `Game Over: ${data.result}`;
            } else {
                document.getElementById('gameStatus').textContent = 
                    'Game in progress';
            }
            
            // Update board
            renderBoard(data.fen);
        })
        .catch(error => {
            console.error('Error updating board:', error);
            showMessage('Error updating board', 'error');
        });
}

function renderBoard(fen) {
    // Remove old pieces
    if (piecesGroup) {
        scene.remove(piecesGroup);
    }
    piecesGroup = new THREE.Group();
    
    // Parse FEN
    const rows = fen.split(' ')[0].split('/');
    
    for (let row = 0; row < 8; row++) {
        let col = 0;
        for (const char of rows[row]) {
            if (char >= '1' && char <= '8') {
                col += parseInt(char);
            } else {
                const color = char === char.toUpperCase() ? 'white' : 'black';
                const piece = createPiece(char.toLowerCase(), color, 7 - row, col);
                piecesGroup.add(piece);
                col++;
            }
        }
    }
    
    scene.add(piecesGroup);
}

function handleClick(intersect) {
    const object = intersect.object;
    
    // Find the top-level object (piece or square)
    let target = object;
    while (target.parent && !target.userData.type) {
        target = target.parent;
    }
    
    if (!target.userData.type) return;
    
    if (target.userData.type === 'piece') {
        selectPiece(target);
    } else if (target.userData.type === 'square') {
        if (selectedPiece) {
            movePiece(target.userData.row, target.userData.col);
        }
    }
}

function selectPiece(piece) {
    // Clear previous selection
    clearHighlights();
    
    selectedPiece = piece;
    selectedSquare = { row: piece.userData.row, col: piece.userData.col };
    
    // Highlight selected piece
    piece.traverse((child) => {
        if (child instanceof THREE.Mesh) {
            child.material = child.material.clone();
            child.material.emissive = new THREE.Color(SELECT_COLOR);
            child.material.emissiveIntensity = 0.3;
        }
    });
    
    // Highlight legal moves for this piece
    const from = String.fromCharCode(97 + selectedSquare.col) + (selectedSquare.row + 1);
    const pieceLegalMoves = legalMoves.filter(move => move.startsWith(from));
    
    pieceLegalMoves.forEach(move => {
        const toCol = move.charCodeAt(2) - 97;
        const toRow = parseInt(move[3]) - 1;
        highlightSquare(toRow, toCol);
    });
}

function highlightSquare(row, col) {
    boardGroup.children.forEach(square => {
        if (square.userData.row === row && square.userData.col === col) {
            square.material = square.material.clone();
            square.material.emissive = new THREE.Color(HIGHLIGHT_COLOR);
            square.material.emissiveIntensity = 0.5;
        }
    });
}

function clearHighlights() {
    // Reset board squares
    boardGroup.children.forEach(square => {
        if (square.userData.type === 'square') {
            const isLight = (square.userData.row + square.userData.col) % 2 === 0;
            square.material = new THREE.MeshStandardMaterial({
                color: isLight ? LIGHT_SQUARE_COLOR : DARK_SQUARE_COLOR
            });
        }
    });
    
    // Reset pieces
    if (piecesGroup) {
        piecesGroup.traverse((child) => {
            if (child instanceof THREE.Mesh && child.material.emissive) {
                child.material.emissive = new THREE.Color(0x000000);
            }
        });
    }
    
    selectedPiece = null;
    selectedSquare = null;
}

function movePiece(toRow, toCol) {
    if (!selectedSquare) return;
    
    const from = String.fromCharCode(97 + selectedSquare.col) + (selectedSquare.row + 1);
    const to = String.fromCharCode(97 + toCol) + (toRow + 1);
    const move = from + to;
    
    // Check for promotion
    let finalMove = move;
    if (selectedPiece.userData.pieceType === 'p' && (toRow === 0 || toRow === 7)) {
        finalMove += 'q'; // Auto-promote to queen
    }
    
    fetch(`${API_URL}/api/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ move: finalMove })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            moveHistory.push(finalMove);
            updateMoveHistory();
            clearHighlights();
            updateBoard();
        } else {
            showMessage(data.error || 'Invalid move', 'error');
            clearHighlights();
        }
    })
    .catch(error => {
        console.error('Error making move:', error);
        showMessage('Error making move', 'error');
        clearHighlights();
    });
}

function updateMoveHistory() {
    const movesDiv = document.getElementById('moves');
    let html = '';
    for (let i = 0; i < moveHistory.length; i += 2) {
        const moveNum = Math.floor(i / 2) + 1;
        const whiteMove = moveHistory[i];
        const blackMove = moveHistory[i + 1] || '';
        html += `<div>${moveNum}. ${whiteMove} ${blackMove}</div>`;
    }
    movesDiv.innerHTML = html;
}

function resetGame() {
    fetch(`${API_URL}/api/reset`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                moveHistory = [];
                updateMoveHistory();
                clearHighlights();
                updateBoard();
                showMessage('Game reset', 'success');
            }
        })
        .catch(error => {
            console.error('Error resetting game:', error);
            showMessage('Error resetting game', 'error');
        });
}

function aiMove() {
    showLoading(true);
    fetch(`${API_URL}/api/ai-move`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                moveHistory.push(data.move);
                updateMoveHistory();
                updateBoard();
                showMessage('AI moved: ' + data.move, 'success');
            } else {
                showMessage(data.error || 'AI move failed', 'error');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error getting AI move:', error);
            showMessage('Error getting AI move', 'error');
        });
}

function changeMode() {
    const mode = document.getElementById('modeSelect').value;
    fetch(`${API_URL}/api/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const modeText = mode === 'player_vs_ai' ? 'Player vs AI' : 'AI vs AI';
            document.getElementById('mode').textContent = modeText;
            showMessage(`Mode changed to ${modeText}`, 'success');
        }
    })
    .catch(error => {
        console.error('Error changing mode:', error);
        showMessage('Error changing mode', 'error');
    });
}

function startSelfPlay() {
    if (selfPlayInterval) return;
    
    document.getElementById('selfPlayBtn').disabled = true;
    document.getElementById('stopPlayBtn').disabled = false;
    
    selfPlayInterval = setInterval(() => {
        fetch(`${API_URL}/api/self-play`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    moveHistory.push(data.move);
                    updateMoveHistory();
                    updateBoard();
                    
                    if (data.is_game_over) {
                        stopSelfPlay();
                        showMessage(`Game over: ${data.result}`, 'success');
                    }
                } else {
                    stopSelfPlay();
                }
            })
            .catch(error => {
                console.error('Error in self-play:', error);
                stopSelfPlay();
            });
    }, 1000);
}

function stopSelfPlay() {
    if (selfPlayInterval) {
        clearInterval(selfPlayInterval);
        selfPlayInterval = null;
    }
    document.getElementById('selfPlayBtn').disabled = false;
    document.getElementById('stopPlayBtn').disabled = true;
}

function saveGame() {
    const filename = document.getElementById('saveFilename').value || undefined;
    showLoading(true);
    fetch(`${API_URL}/api/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            showMessage(`Game saved as ${data.filename}`, 'success');
            loadGamesList();
        } else {
            showMessage('Error saving game', 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error saving game:', error);
        showMessage('Error saving game', 'error');
    });
}

function loadGame() {
    const filename = document.getElementById('loadSelect').value;
    if (!filename) {
        showMessage('Please select a game to load', 'error');
        return;
    }
    
    showLoading(true);
    fetch(`${API_URL}/api/load`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            updateBoard();
            showMessage(`Game loaded from ${filename}`, 'success');
        } else {
            showMessage('Error loading game', 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error loading game:', error);
        showMessage('Error loading game', 'error');
    });
}

function loadGamesList() {
    fetch(`${API_URL}/api/games`)
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('loadSelect');
            select.innerHTML = '<option value="">Select game...</option>';
            data.games.forEach(game => {
                const option = document.createElement('option');
                option.value = game;
                option.textContent = game;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading games list:', error);
        });
}

function trainAI() {
    showLoading(true);
    fetch(`${API_URL}/api/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ epochs: 10 })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.success) {
            showMessage('AI training completed', 'success');
        } else {
            showMessage('Error training AI', 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error training AI:', error);
        showMessage('Error training AI', 'error');
    });
}

function saveModel() {
    showLoading(true);
    fetch(`${API_URL}/api/model/save`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showMessage('Model saved successfully', 'success');
            } else {
                showMessage('Error saving model', 'error');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error saving model:', error);
            showMessage('Error saving model', 'error');
        });
}

function loadModel() {
    showLoading(true);
    fetch(`${API_URL}/api/model/load`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                showMessage('Model loaded successfully', 'success');
            } else {
                showMessage('Error loading model', 'error');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error loading model:', error);
            showMessage('Error loading model', 'error');
        });
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    messageDiv.style.display = 'block';
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 3000);
}

function showLoading(show) {
    const loadingDiv = document.getElementById('loading');
    loadingDiv.className = show ? '' : 'hidden';
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
