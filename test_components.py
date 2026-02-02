#!/usr/bin/env python3
"""
Test script to verify all components work correctly
"""

import sys

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        import chess
        print("✓ chess library")
    except ImportError as e:
        print(f"✗ chess library: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy")
    except ImportError as e:
        print(f"✗ numpy: {e}")
        return False
    
    try:
        from PyQt5 import QtWidgets, QtCore, QtGui
        print("✓ PyQt5")
    except ImportError as e:
        print(f"✗ PyQt5: {e}")
        return False
    
    try:
        from OpenGL import GL, GLU
        print("✓ PyOpenGL")
    except ImportError as e:
        print(f"✗ PyOpenGL: {e}")
        return False
    
    try:
        import tensorflow
        print("✓ TensorFlow (optional - for AI training)")
    except ImportError:
        print("- TensorFlow not installed (optional - AI will use basic evaluation)")
    
    return True

def test_chess_ai():
    """Test chess AI functionality"""
    print("\nTesting Chess AI...")
    
    try:
        from chess_ai import ChessAI
        import chess
        
        ai = ChessAI()
        board = chess.Board()
        
        # Test move generation
        move = ai.get_best_move(board)
        if move and move in board.legal_moves:
            print(f"✓ AI generated legal move: {move}")
        else:
            print("✗ AI failed to generate legal move")
            return False
        
        # Test position evaluation
        eval_score = ai.evaluate_position(board)
        print(f"✓ Position evaluation: {eval_score}")
        
        return True
    except Exception as e:
        print(f"✗ Chess AI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pgn():
    """Test PGN save/load functionality"""
    print("\nTesting PGN functionality...")
    
    try:
        import chess
        import chess.pgn
        from datetime import datetime
        import os
        
        # Create a simple game
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        
        # Create PGN
        game = chess.pgn.Game()
        game.headers["Event"] = "Test Game"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        
        node = game
        test_board = chess.Board()
        for move in board.move_stack:
            node = node.add_variation(move)
        
        # Test PGN string generation
        pgn_string = str(game)
        if "e2e4" in pgn_string or "e4" in pgn_string:
            print("✓ PGN generation works")
        else:
            print("✗ PGN generation failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ PGN test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("3D Chess AI - Component Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        print("\n⚠ Some imports failed. Install with: pip install -r requirements.txt")
    
    # Test chess AI
    if not test_chess_ai():
        all_passed = False
    
    # Test PGN
    if not test_pgn():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed!")
        print("\nYou can now run the application:")
        print("  python main.py")
        print("\nOr build the executable:")
        print("  pyinstaller ChessAI.spec")
        return 0
    else:
        print("✗ Some tests failed")
        print("\nPlease fix the issues before running the application.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
