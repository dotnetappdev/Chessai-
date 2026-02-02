import chess
import chess.pgn
import numpy as np
import random
import os
import pickle
from typing import Optional, List, Tuple, Any
from io import StringIO

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
    
    # Training constants
    MIN_BATCH_SIZE = 32  # Minimum positions needed for training
    GAMES_BEFORE_TRAINING = 5  # Train after this many completed games (normal mode)
    MOVE_WEIGHT_THRESHOLD = 40.0  # Moves before full outcome weight applied
    
    def __init__(self, model_path: str = 'models/chess_ai.keras', auto_train: bool = True, 
                 train_every_game: bool = False):
        self.model_path = model_path
        self.model = None
        self.training_data = []
        self.max_training_data = 10000
        self.auto_train = auto_train
        self.train_every_game = train_every_game  # If True, train after every game (for self-play)
        self.games_since_training = 0
        self.games_before_training = 1 if train_every_game else self.GAMES_BEFORE_TRAINING
        
        # Load initial training data if available
        self._load_initial_training_data()
        
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
    
    def _load_initial_training_data(self):
        """Load initial training data from example games if available"""
        initial_data_path = 'models/initial_training_data.pkl'
        if os.path.exists(initial_data_path):
            try:
                with open(initial_data_path, 'rb') as f:
                    initial_data = pickle.load(f)
                self.training_data = initial_data[:self.max_training_data]
                print(f"Loaded {len(self.training_data)} initial training positions from example games")
            except Exception as e:
                print(f"Could not load initial training data: {e}")
    
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
    
    def on_game_complete(self, result: str):
        """Called when a game completes - triggers automatic training if enabled"""
        if not HAS_TENSORFLOW or not self.auto_train:
            return
        
        self.games_since_training += 1
        
        # Train after accumulating enough games
        if self.games_since_training >= self.games_before_training:
            if len(self.training_data) >= self.MIN_BATCH_SIZE:
                print(f"Auto-training after {self.games_since_training} games...")
                try:
                    self.train(epochs=5, batch_size=self.MIN_BATCH_SIZE)
                    self.save_model()
                    print("Auto-training completed and model saved.")
                except Exception as e:
                    print(f"Auto-training failed: {e}")
                self.games_since_training = 0
    
    def learn_from_pgn_file(self, pgn_file_path: str) -> int:
        """Learn from a PGN file containing chess games (e.g., grandmaster games)
        
        Supports standard PGN format compatible with Chess.com, Lichess, ChessBase, etc.
        Games should include Result header (1-0, 0-1, 1/2-1/2, or *).
        
        Args:
            pgn_file_path: Path to PGN file
            
        Returns:
            Number of positions added to training data
        """
        if not os.path.exists(pgn_file_path):
            raise FileNotFoundError(f"PGN file not found: {pgn_file_path}")
        
        positions_added = 0
        
        with open(pgn_file_path, 'r') as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                # Get result to determine evaluation
                result = game.headers.get("Result", "*")
                
                # Determine outcome value
                if result == "1-0":  # White wins
                    outcome_value = 1.0
                elif result == "0-1":  # Black wins
                    outcome_value = -1.0
                else:  # Draw or unknown
                    outcome_value = 0.0
                
                # Replay game and record positions
                board = chess.Board()
                move_count = 0
                
                for move in game.mainline_moves():
                    # Record position before move
                    tensor = self.board_to_tensor(board)
                    
                    # Evaluation tapers based on move count and outcome
                    # Early game (moves 0-40): gradually increase weight toward outcome
                    # This reflects that early moves matter less for final result
                    move_weight = min(1.0, move_count / self.MOVE_WEIGHT_THRESHOLD)
                    eval_value = outcome_value * move_weight
                    
                    self.training_data.append((tensor, eval_value))
                    positions_added += 1
                    
                    # Limit training data size
                    if len(self.training_data) > self.max_training_data:
                        self.training_data.pop(0)
                    
                    board.push(move)
                    move_count += 1
        
        return positions_added
    
    def learn_from_pgn_string(self, pgn_string: str) -> int:
        """Learn from a PGN string containing chess games
        
        Args:
            pgn_string: PGN formatted string
            
        Returns:
            Number of positions added to training data
        """
        positions_added = 0
        pgn_io = StringIO(pgn_string)
        
        while True:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
            
            # Get result to determine evaluation
            result = game.headers.get("Result", "*")
            
            # Determine outcome value
            if result == "1-0":  # White wins
                outcome_value = 1.0
            elif result == "0-1":  # Black wins
                outcome_value = -1.0
            else:  # Draw or unknown
                outcome_value = 0.0
            
            # Replay game and record positions
            board = chess.Board()
            move_count = 0
            
            for move in game.mainline_moves():
                # Record position before move
                tensor = self.board_to_tensor(board)
                
                # Evaluation tapers based on move count and outcome
                move_weight = min(1.0, move_count / self.MOVE_WEIGHT_THRESHOLD)
                eval_value = outcome_value * move_weight
                
                self.training_data.append((tensor, eval_value))
                positions_added += 1
                
                # Limit training data size
                if len(self.training_data) > self.max_training_data:
                    self.training_data.pop(0)
                
                board.push(move)
                move_count += 1
        
        return positions_added
    
    def get_training_data_size(self) -> int:
        """Get the current size of training data"""
        return len(self.training_data)
