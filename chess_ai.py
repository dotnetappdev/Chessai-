import chess
import numpy as np
import random
import os
from typing import Optional, List, Tuple, Any

# Try to import TensorFlow, but make it optional
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    keras = None  # For type hints
    print("Warning: TensorFlow not available. AI will use basic evaluation only.")

class ChessAI:
    """Chess AI with learning capabilities"""
    
    def __init__(self, model_path: str = 'models/chess_ai.keras'):
        self.model_path = model_path
        self.model = None
        self.training_data = []
        self.max_training_data = 10000
        
        # Only try to use neural network if TensorFlow is available
        if HAS_TENSORFLOW:
            # Try to load existing model
            if os.path.exists(model_path):
                try:
                    self.load_model()
                except:
                    self.model = self._build_model()
            else:
                self.model = self._build_model()
        else:
            print("Running without neural network - using material evaluation only")
    
    def _build_model(self) -> Optional[Any]:
        """Build neural network model for chess evaluation"""
        if not HAS_TENSORFLOW:
            return None
            
        model = keras.Sequential([
            layers.Input(shape=(8, 8, 12)),  # 8x8 board, 12 piece types
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dense(1, activation='tanh')  # Output: position evaluation
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def board_to_tensor(self, board: chess.Board) -> np.ndarray:
        """Convert chess board to tensor representation"""
        tensor = np.zeros((8, 8, 12), dtype=np.float32)
        
        piece_idx = {
            chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 2,
            chess.ROOK: 3, chess.QUEEN: 4, chess.KING: 5
        }
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                idx = piece_idx[piece.piece_type]
                if piece.color == chess.BLACK:
                    idx += 6
                tensor[rank][file][idx] = 1.0
        
        return tensor
    
    def evaluate_position(self, board: chess.Board) -> float:
        """Evaluate board position using neural network"""
        if self.model is None:
            return self._material_evaluation(board)
        
        try:
            tensor = self.board_to_tensor(board)
            tensor = np.expand_dims(tensor, axis=0)
            evaluation = self.model.predict(tensor, verbose=0)[0][0]
            return float(evaluation)
        except:
            return self._material_evaluation(board)
    
    def _material_evaluation(self, board: chess.Board) -> float:
        """Simple material-based evaluation"""
        if board.is_checkmate():
            return -999 if board.turn else 999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }
        
        value = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                piece_value = piece_values[piece.piece_type]
                value += piece_value if piece.color == chess.WHITE else -piece_value
        
        # Add positional bonuses
        value += len(list(board.legal_moves)) * 0.1 if board.turn == chess.WHITE else -0.1
        
        return value
    
    def get_best_move(self, board: chess.Board, depth: int = 2) -> Optional[chess.Move]:
        """Get best move using minimax with alpha-beta pruning"""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        best_move = None
        best_value = float('-inf') if board.turn == chess.WHITE else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Add some randomness to make play more interesting
        random.shuffle(legal_moves)
        
        for move in legal_moves:
            board.push(move)
            value = self._minimax(board, depth - 1, alpha, beta, not board.turn)
            board.pop()
            
            if board.turn == chess.WHITE:
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, value)
            else:
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, value)
        
        # Store position for training
        self._record_position(board, best_move, best_value)
        
        return best_move
    
    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                 maximizing: bool) -> float:
        """Minimax algorithm with alpha-beta pruning"""
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board)
        
        legal_moves = list(board.legal_moves)
        
        if maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                board.push(move)
                eval = self._minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval = self._minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def _record_position(self, board: chess.Board, move: chess.Move, evaluation: float):
        """Record position for training"""
        tensor = self.board_to_tensor(board)
        self.training_data.append((tensor, evaluation))
        
        # Limit training data size
        if len(self.training_data) > self.max_training_data:
            self.training_data.pop(0)
    
    def train(self, epochs: int = 10, batch_size: int = 32) -> dict:
        """Train the model on recorded positions"""
        if not HAS_TENSORFLOW:
            return {'loss': [], 'mae': [], 'error': 'TensorFlow not available'}
            
        if len(self.training_data) < batch_size:
            return {'loss': [], 'mae': []}
        
        X = np.array([data[0] for data in self.training_data])
        y = np.array([data[1] for data in self.training_data])
        
        # Normalize evaluations
        y = np.clip(y, -10, 10) / 10.0
        
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        return {
            'loss': history.history['loss'],
            'mae': history.history['mae']
        }
    
    def save_model(self):
        """Save model to disk"""
        if not HAS_TENSORFLOW or self.model is None:
            raise Exception("TensorFlow not available or model not initialized")
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.model.save(self.model_path)
    
    def load_model(self):
        """Load model from disk"""
        if not HAS_TENSORFLOW:
            raise Exception("TensorFlow not available")
        if os.path.exists(self.model_path):
            self.model = keras.models.load_model(self.model_path)
