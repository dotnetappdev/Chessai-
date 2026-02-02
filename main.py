#!/usr/bin/env python3
"""
3D Chess AI - Desktop Application
A standalone chess game with 3D graphics and AI opponent
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QFileDialog, QMessageBox, QGroupBox, QLineEdit,
                             QTextEdit, QProgressDialog)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont
import chess
import chess.pgn
from chess_ai import ChessAI
from chess_board_3d import ChessBoard3D
from datetime import datetime


class ChessGameWindow(QMainWindow):
    """Main window for the chess game application"""
    
    def __init__(self):
        super().__init__()
        self.board = chess.Board()
        self.ai = ChessAI()
        self.game_mode = "player_vs_ai"
        self.self_play_timer = None
        self.move_history = []
        
        self.init_ui()
        self.update_status()
        self.update_training_data_label()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('3D Chess AI')
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - 3D Chess Board
        self.chess_board_3d = ChessBoard3D(self.board, self)
        self.chess_board_3d.move_made.connect(self.on_player_move)
        main_layout.addWidget(self.chess_board_3d, stretch=3)
        
        # Right panel - Controls
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        right_panel.setMaximumWidth(400)
        main_layout.addWidget(right_panel, stretch=1)
        
        # Title
        title = QLabel('3D Chess AI')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(title)
        
        # Status group
        status_group = QGroupBox('Game Status')
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        self.turn_label = QLabel('Turn: White')
        self.turn_label.setFont(QFont('Arial', 12))
        status_layout.addWidget(self.turn_label)
        
        self.mode_label = QLabel('Mode: Player vs AI')
        self.mode_label.setFont(QFont('Arial', 12))
        status_layout.addWidget(self.mode_label)
        
        self.status_label = QLabel('Game in progress')
        self.status_label.setFont(QFont('Arial', 12))
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        right_layout.addWidget(status_group)
        
        # Game mode group
        mode_group = QGroupBox('Game Mode')
        mode_layout = QVBoxLayout()
        mode_group.setLayout(mode_layout)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItem('Player vs AI', 'player_vs_ai')
        self.mode_combo.addItem('AI vs AI', 'ai_vs_ai')
        mode_layout.addWidget(self.mode_combo)
        
        change_mode_btn = QPushButton('Change Mode')
        change_mode_btn.clicked.connect(self.change_mode)
        mode_layout.addWidget(change_mode_btn)
        
        right_layout.addWidget(mode_group)
        
        # Game controls group
        controls_group = QGroupBox('Game Controls')
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)
        
        new_game_btn = QPushButton('New Game')
        new_game_btn.clicked.connect(self.new_game)
        controls_layout.addWidget(new_game_btn)
        
        ai_move_btn = QPushButton('AI Move')
        ai_move_btn.clicked.connect(self.make_ai_move)
        controls_layout.addWidget(ai_move_btn)
        
        right_layout.addWidget(controls_group)
        
        # Self-play group
        selfplay_group = QGroupBox('AI Self-Play')
        selfplay_layout = QVBoxLayout()
        selfplay_group.setLayout(selfplay_layout)
        
        self.start_selfplay_btn = QPushButton('Start Self-Play')
        self.start_selfplay_btn.clicked.connect(self.start_self_play)
        selfplay_layout.addWidget(self.start_selfplay_btn)
        
        self.stop_selfplay_btn = QPushButton('Stop Self-Play')
        self.stop_selfplay_btn.clicked.connect(self.stop_self_play)
        self.stop_selfplay_btn.setEnabled(False)
        selfplay_layout.addWidget(self.stop_selfplay_btn)
        
        right_layout.addWidget(selfplay_group)
        
        # Save/Load group
        saveload_group = QGroupBox('Save/Load Game')
        saveload_layout = QVBoxLayout()
        saveload_group.setLayout(saveload_layout)
        
        save_btn = QPushButton('Save Game (PGN)')
        save_btn.clicked.connect(self.save_game)
        saveload_layout.addWidget(save_btn)
        
        load_btn = QPushButton('Load Game (PGN)')
        load_btn.clicked.connect(self.load_game)
        saveload_layout.addWidget(load_btn)
        
        right_layout.addWidget(saveload_group)
        
        # AI Training group
        training_group = QGroupBox('AI Training')
        training_layout = QVBoxLayout()
        training_group.setLayout(training_layout)
        
        # Auto-train label
        self.training_data_label = QLabel('Training data: 0 positions')
        training_layout.addWidget(self.training_data_label)
        
        train_btn = QPushButton('Train AI (10 epochs)')
        train_btn.clicked.connect(self.train_ai)
        training_layout.addWidget(train_btn)
        
        # Load grandmaster games button
        load_pgn_btn = QPushButton('Learn from PGN File')
        load_pgn_btn.clicked.connect(self.load_pgn_for_training)
        training_layout.addWidget(load_pgn_btn)
        
        save_model_btn = QPushButton('Save Model')
        save_model_btn.clicked.connect(self.save_model)
        training_layout.addWidget(save_model_btn)
        
        load_model_btn = QPushButton('Load Model')
        load_model_btn.clicked.connect(self.load_model)
        training_layout.addWidget(load_model_btn)
        
        right_layout.addWidget(training_group)
        
        # Move history
        history_group = QGroupBox('Move History')
        history_layout = QVBoxLayout()
        history_group.setLayout(history_layout)
        
        self.move_history_text = QTextEdit()
        self.move_history_text.setReadOnly(True)
        self.move_history_text.setMaximumHeight(150)
        history_layout.addWidget(self.move_history_text)
        
        right_layout.addWidget(history_group)
        
        # Add stretch to push everything up
        right_layout.addStretch()
        
    def on_player_move(self, move_uci):
        """Handle player move from 3D board"""
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move_uci)
                self.update_move_history()
                self.update_status()
                self.chess_board_3d.update_board(self.board)
                
                # Check if game is over after this move
                if self.board.is_game_over():
                    self.on_game_complete()
                elif self.game_mode == "player_vs_ai":
                    # Make AI response move
                    QTimer.singleShot(500, self.make_ai_move)
            else:
                QMessageBox.warning(self, 'Invalid Move', 'That move is not legal!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error making move: {str(e)}')
    
    def make_ai_move(self):
        """Make an AI move"""
        if self.board.is_game_over():
            return
        
        try:
            move = self.ai.get_best_move(self.board)
            if move:
                self.board.push(move)
                self.move_history.append(move.uci())
                self.update_move_history()
                self.update_status()
                self.chess_board_3d.update_board(self.board)
                
                # Check if game is over after AI move
                if self.board.is_game_over():
                    self.on_game_complete()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'AI move error: {str(e)}')
    
    def on_game_complete(self):
        """Called when a game completes"""
        result = self.board.result()
        # Trigger AI auto-training
        self.ai.on_game_complete(result)
        # Update training data label
        self.update_training_data_label()
    
    def new_game(self):
        """Start a new game"""
        reply = QMessageBox.question(self, 'New Game', 
                                     'Start a new game? Current game will be lost.',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Check if current game is complete and trigger training
            if self.board.move_stack and self.board.is_game_over():
                self.on_game_complete()
            
            self.board = chess.Board()
            self.move_history = []
            self.update_move_history()
            self.update_status()
            self.chess_board_3d.update_board(self.board)
            self.stop_self_play()
    
    def change_mode(self):
        """Change game mode"""
        mode_data = self.mode_combo.currentData()
        self.game_mode = mode_data
        mode_text = self.mode_combo.currentText()
        self.mode_label.setText(f'Mode: {mode_text}')
        QMessageBox.information(self, 'Mode Changed', f'Game mode changed to {mode_text}')
    
    def start_self_play(self):
        """Start AI self-play"""
        if self.self_play_timer is not None:
            return
        
        self.start_selfplay_btn.setEnabled(False)
        self.stop_selfplay_btn.setEnabled(True)
        
        self.self_play_timer = QTimer()
        self.self_play_timer.timeout.connect(self.self_play_move)
        self.self_play_timer.start(1000)  # 1 move per second
    
    def stop_self_play(self):
        """Stop AI self-play"""
        if self.self_play_timer is not None:
            self.self_play_timer.stop()
            self.self_play_timer = None
        
        self.start_selfplay_btn.setEnabled(True)
        self.stop_selfplay_btn.setEnabled(False)
    
    def self_play_move(self):
        """Make one self-play move"""
        if self.board.is_game_over():
            self.on_game_complete()
            self.stop_self_play()
            return
        
        self.make_ai_move()
    
    def save_game(self):
        """Save game to PGN file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Save Game', 
            f'game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pgn',
            'PGN Files (*.pgn)'
        )
        
        if filename:
            try:
                game = chess.pgn.Game()
                game.headers["Event"] = "Chess AI Game"
                game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
                game.headers["White"] = "Player/AI"
                game.headers["Black"] = "AI"
                
                # Add moves
                node = game
                temp_board = chess.Board()
                for move in self.board.move_stack:
                    node = node.add_variation(move)
                
                with open(filename, 'w') as f:
                    f.write(str(game))
                
                QMessageBox.information(self, 'Success', f'Game saved to {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error saving game: {str(e)}')
    
    def load_game(self):
        """Load game from PGN file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Load Game', '', 'PGN Files (*.pgn)'
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    game = chess.pgn.read_game(f)
                
                if game:
                    self.board = chess.Board()
                    self.move_history = []
                    
                    for move in game.mainline_moves():
                        self.board.push(move)
                        self.move_history.append(move.uci())
                    
                    self.update_move_history()
                    self.update_status()
                    self.chess_board_3d.update_board(self.board)
                    QMessageBox.information(self, 'Success', f'Game loaded from {filename}')
                else:
                    QMessageBox.warning(self, 'Error', 'Could not parse PGN file')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error loading game: {str(e)}')
    
    def train_ai(self):
        """Train the AI"""
        progress = QProgressDialog('Training AI...', 'Cancel', 0, 10, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            history = self.ai.train(epochs=10)
            progress.setValue(10)
            
            loss = history.get('loss', [])
            final_loss = loss[-1] if loss else 'N/A'
            self.update_training_data_label()
            QMessageBox.information(self, 'Training Complete', 
                                   f'AI training completed!\nFinal loss: {final_loss:.4f}' if isinstance(final_loss, float) else 'AI training completed!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error training AI: {str(e)}')
        finally:
            progress.close()
    
    def load_pgn_for_training(self):
        """Load PGN file to train AI from grandmaster games"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Load PGN for Training', '', 'PGN Files (*.pgn);;All Files (*)'
        )
        
        if filename:
            progress = QProgressDialog('Learning from PGN file...', 'Cancel', 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            try:
                positions_added = self.ai.learn_from_pgn_file(filename)
                progress.close()
                self.update_training_data_label()
                
                QMessageBox.information(self, 'Success', 
                                       f'Loaded {positions_added} positions from PGN file!\n'
                                       f'Total training data: {self.ai.get_training_data_size()} positions\n\n'
                                       f'Click "Train AI" to train the model with this data.')
            except Exception as e:
                progress.close()
                QMessageBox.critical(self, 'Error', f'Error loading PGN for training: {str(e)}')
    
    def update_training_data_label(self):
        """Update the training data label"""
        data_size = self.ai.get_training_data_size()
        self.training_data_label.setText(f'Training data: {data_size} positions')
    
    def save_model(self):
        """Save AI model"""
        try:
            self.ai.save_model()
            QMessageBox.information(self, 'Success', 'AI model saved successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error saving model: {str(e)}')
    
    def load_model(self):
        """Load AI model"""
        try:
            self.ai.load_model()
            QMessageBox.information(self, 'Success', 'AI model loaded successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error loading model: {str(e)}')
    
    def update_status(self):
        """Update status labels"""
        turn = 'White' if self.board.turn == chess.WHITE else 'Black'
        self.turn_label.setText(f'Turn: {turn}')
        
        if self.board.is_checkmate():
            winner = 'Black' if self.board.turn == chess.WHITE else 'White'
            self.status_label.setText(f'Checkmate! {winner} wins!')
        elif self.board.is_stalemate():
            self.status_label.setText('Stalemate! Draw.')
        elif self.board.is_insufficient_material():
            self.status_label.setText('Draw by insufficient material.')
        elif self.board.is_game_over():
            self.status_label.setText(f'Game Over: {self.board.result()}')
        else:
            self.status_label.setText('Game in progress')
    
    def update_move_history(self):
        """Update move history display"""
        history_text = ''
        for i in range(0, len(self.move_history), 2):
            move_num = i // 2 + 1
            white_move = self.move_history[i]
            black_move = self.move_history[i + 1] if i + 1 < len(self.move_history) else ''
            history_text += f'{move_num}. {white_move} {black_move}\n'
        
        self.move_history_text.setPlainText(history_text)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = ChessGameWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
