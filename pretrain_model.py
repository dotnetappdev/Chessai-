#!/usr/bin/env python3
"""
Pre-train the chess AI model using the example games

NOTE: This script requires TensorFlow to be installed.
If TensorFlow is not available, the AI will still work using
classical chess evaluation (material + position).

Install TensorFlow with: pip install tensorflow
"""

import sys
import os

# Try to import TensorFlow
try:
    import tensorflow as tf
    print("TensorFlow available - proceeding with pre-training")
    HAS_TF = True
except ImportError:
    print("=" * 60)
    print("TensorFlow is not installed")
    print("=" * 60)
    print("\nThe AI can still work without TensorFlow using classical evaluation.")
    print("To enable neural network learning, install TensorFlow:")
    print("  pip install tensorflow")
    print("\nWithout TensorFlow, the AI uses material + mobility evaluation")
    print("which is still functional but won't improve through training.")
    print("=" * 60)
    HAS_TF = False

from chess_ai import ChessAI

def pretrain_model():
    """Pre-train the model with example games"""
    if not HAS_TF:
        return False
    
    print("=" * 60)
    print("Chess AI Pre-Training Script")
    print("=" * 60)
    
    # Create AI instance
    print("\n1. Initializing AI...")
    ai = ChessAI(auto_train=False)  # Disable auto-train during pre-training
    
    # Load example games
    print("\n2. Loading example games from example_games.pgn...")
    try:
        positions_added = ai.learn_from_pgn_file('example_games.pgn')
        print(f"   ✓ Loaded {positions_added} positions from example games")
    except Exception as e:
        print(f"   ✗ Error loading example games: {e}")
        return False
    
    # Check if we have enough data
    if ai.get_training_data_size() < ai.MIN_BATCH_SIZE:
        print(f"\n   ✗ Not enough training data (need at least {ai.MIN_BATCH_SIZE})")
        return False
    
    print(f"   ✓ Total training data: {ai.get_training_data_size()} positions")
    
    # Train the model
    print("\n3. Training the model (this may take a few minutes)...")
    try:
        # Train for more epochs during pre-training for better initial performance
        history = ai.train(epochs=20, batch_size=32)
        
        loss = history.get('loss', [])
        if loss:
            print(f"   ✓ Training completed!")
            print(f"   Initial loss: {loss[0]:.4f}")
            print(f"   Final loss: {loss[-1]:.4f}")
        else:
            print(f"   ✓ Training completed!")
    except Exception as e:
        print(f"   ✗ Training error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save the model
    print("\n4. Saving pre-trained model...")
    try:
        ai.save_model()
        print(f"   ✓ Model saved to {ai.model_path}")
    except Exception as e:
        print(f"   ✗ Error saving model: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("Pre-training completed successfully!")
    print("=" * 60)
    print("\nThe AI now has a pre-trained model based on famous chess games.")
    print("Run 'python main.py' to use the application with the pre-trained AI.")
    print("\n")
    
    return True

if __name__ == '__main__':
    success = pretrain_model()
    sys.exit(0 if success else 1)
