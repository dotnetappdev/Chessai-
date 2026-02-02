from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import chess
import chess.pgn
from chess_ai import ChessAI
import io
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize chess game and AI
board = chess.Board()
ai = ChessAI()

# Game state
game_mode = "player_vs_ai"  # "player_vs_ai" or "ai_vs_ai"
current_pgn = None

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/board', methods=['GET'])
def get_board():
    """Get current board state"""
    return jsonify({
        'fen': board.fen(),
        'legal_moves': [move.uci() for move in board.legal_moves],
        'is_game_over': board.is_game_over(),
        'result': board.result() if board.is_game_over() else None,
        'turn': 'white' if board.turn == chess.WHITE else 'black'
    })

@app.route('/api/move', methods=['POST'])
def make_move():
    """Make a move on the board"""
    data = request.json
    move_uci = data.get('move')
    
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            
            # If in player vs AI mode, make AI move
            if game_mode == "player_vs_ai" and not board.is_game_over():
                ai_move = ai.get_best_move(board)
                if ai_move:
                    board.push(ai_move)
            
            return jsonify({
                'success': True,
                'fen': board.fen(),
                'is_game_over': board.is_game_over(),
                'result': board.result() if board.is_game_over() else None,
                'turn': 'white' if board.turn == chess.WHITE else 'black'
            })
        else:
            return jsonify({'success': False, 'error': 'Illegal move'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ai-move', methods=['POST'])
def ai_move():
    """Make an AI move"""
    if board.is_game_over():
        return jsonify({'success': False, 'error': 'Game is over'}), 400
    
    move = ai.get_best_move(board)
    if move:
        board.push(move)
        return jsonify({
            'success': True,
            'move': move.uci(),
            'fen': board.fen(),
            'is_game_over': board.is_game_over(),
            'result': board.result() if board.is_game_over() else None,
            'turn': 'white' if board.turn == chess.WHITE else 'black'
        })
    
    return jsonify({'success': False, 'error': 'No legal moves'}), 400

@app.route('/api/reset', methods=['POST'])
def reset_board():
    """Reset the board to starting position"""
    global board
    board = chess.Board()
    return jsonify({'success': True, 'fen': board.fen()})

@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Set game mode"""
    global game_mode
    data = request.json
    mode = data.get('mode')
    
    if mode in ['player_vs_ai', 'ai_vs_ai']:
        game_mode = mode
        return jsonify({'success': True, 'mode': game_mode})
    
    return jsonify({'success': False, 'error': 'Invalid mode'}), 400

@app.route('/api/mode', methods=['GET'])
def get_mode():
    """Get current game mode"""
    return jsonify({'mode': game_mode})

@app.route('/api/self-play', methods=['POST'])
def self_play():
    """Start AI self-play"""
    if board.is_game_over():
        return jsonify({'success': False, 'error': 'Game is over'}), 400
    
    move = ai.get_best_move(board)
    if move:
        board.push(move)
        return jsonify({
            'success': True,
            'move': move.uci(),
            'fen': board.fen(),
            'is_game_over': board.is_game_over(),
            'result': board.result() if board.is_game_over() else None,
            'turn': 'white' if board.turn == chess.WHITE else 'black'
        })
    
    return jsonify({'success': False, 'error': 'No legal moves'}), 400

@app.route('/api/save', methods=['POST'])
def save_game():
    """Save game to PGN format"""
    data = request.json
    filename = data.get('filename', f'game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pgn')
    
    # Create PGN
    game = chess.pgn.Game()
    game.headers["Event"] = "Chess AI Game"
    game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    game.headers["White"] = "Player/AI"
    game.headers["Black"] = "AI"
    
    # Add moves
    node = game
    temp_board = chess.Board()
    for move in board.move_stack:
        node = node.add_variation(move)
    
    # Save to file
    os.makedirs('games', exist_ok=True)
    filepath = os.path.join('games', filename)
    with open(filepath, 'w') as f:
        f.write(str(game))
    
    return jsonify({'success': True, 'filename': filename})

@app.route('/api/load', methods=['POST'])
def load_game():
    """Load game from PGN format"""
    global board
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'success': False, 'error': 'Filename required'}), 400
    
    filepath = os.path.join('games', filename)
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    try:
        with open(filepath, 'r') as f:
            game = chess.pgn.read_game(f)
        
        # Reset board and replay moves
        board = chess.Board()
        for move in game.mainline_moves():
            board.push(move)
        
        return jsonify({
            'success': True,
            'fen': board.fen(),
            'is_game_over': board.is_game_over(),
            'result': board.result() if board.is_game_over() else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/games', methods=['GET'])
def list_games():
    """List saved games"""
    games_dir = 'games'
    if not os.path.exists(games_dir):
        return jsonify({'games': []})
    
    files = [f for f in os.listdir(games_dir) if f.endswith('.pgn')]
    return jsonify({'games': files})

@app.route('/api/train', methods=['POST'])
def train_ai():
    """Train AI model"""
    data = request.json
    epochs = data.get('epochs', 10)
    
    try:
        history = ai.train(epochs=epochs)
        return jsonify({
            'success': True,
            'message': f'Training completed for {epochs} epochs',
            'loss': history.get('loss', [])[-1] if history.get('loss') else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/model/save', methods=['POST'])
def save_model():
    """Save AI model"""
    try:
        ai.save_model()
        return jsonify({'success': True, 'message': 'Model saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/model/load', methods=['POST'])
def load_model():
    """Load AI model"""
    try:
        ai.load_model()
        return jsonify({'success': True, 'message': 'Model loaded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
