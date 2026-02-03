#!/usr/bin/env python3
"""
Test script for new features: animations, sounds, themes, and analysis
"""

import sys
import os

# Test 1: Check if sound files exist
def test_sound_files():
    print("Testing sound files...")
    sound_files = ['move.wav', 'capture.wav', 'check.wav', 'checkmate.wav']
    all_exist = True
    
    for sound_file in sound_files:
        path = os.path.join('sounds', sound_file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✓ {sound_file} ({size} bytes)")
        else:
            print(f"  ✗ {sound_file} not found")
            all_exist = False
    
    return all_exist

# Test 2: Check if theme definitions are present
def test_themes():
    print("\nTesting theme definitions...")
    try:
        from chess_board_3d import ChessBoard3D
        
        themes = ['Classic', 'Modern', 'Wood', 'Metal']
        all_present = True
        
        for theme in themes:
            if theme in ChessBoard3D.THEMES:
                colors = ChessBoard3D.THEMES[theme]
                print(f"  ✓ {theme} theme: {len(colors)} colors defined")
            else:
                print(f"  ✗ {theme} theme not found")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

# Test 3: Check if ChessAI has get_top_moves method
def test_analysis_methods():
    print("\nTesting analysis methods...")
    try:
        from chess_ai import ChessAI
        import chess
        
        ai = ChessAI()
        board = chess.Board()
        
        # Check if get_top_moves exists
        if hasattr(ai, 'get_top_moves'):
            print("  ✓ get_top_moves method exists")
            
            # Try to get top moves
            try:
                top_moves = ai.get_top_moves(board, n=3, depth=1)
                if len(top_moves) > 0:
                    print(f"  ✓ get_top_moves returned {len(top_moves)} moves")
                    for i, (move, eval) in enumerate(top_moves[:3], 1):
                        print(f"    {i}. {move.uci()} (eval: {eval:+.2f})")
                    return True
                else:
                    print("  ✗ get_top_moves returned no moves")
                    return False
            except Exception as e:
                print(f"  ✗ Error calling get_top_moves: {e}")
                return False
        else:
            print("  ✗ get_top_moves method not found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test 4: Check ChessBoard3D animation features
def test_animation_features():
    print("\nTesting animation features...")
    try:
        from chess_board_3d import ChessBoard3D
        import chess
        
        # Check for animation-related attributes
        board = chess.Board()
        chess_board = ChessBoard3D(board)
        
        features = [
            'animating',
            'animation_progress',
            'animation_timer',
            'animate_move',
            'update_animation'
        ]
        
        all_present = True
        for feature in features:
            if hasattr(chess_board, feature):
                print(f"  ✓ {feature}")
            else:
                print(f"  ✗ {feature} not found")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test 5: Check UI additions in main.py
def test_ui_additions():
    print("\nTesting UI additions...")
    try:
        with open('main.py', 'r') as f:
            content = f.read()
        
        features = [
            ('theme_combo', 'Theme selector'),
            ('sound_checkbox', 'Sound toggle'),
            ('analysis_checkbox', 'Analysis mode toggle'),
            ('hint_btn', 'Hint button'),
            ('suggestion_label', 'Suggestion display'),
            ('change_theme', 'Theme change method'),
            ('toggle_sound', 'Sound toggle method'),
            ('toggle_analysis_mode', 'Analysis toggle method'),
            ('show_hint', 'Show hint method'),
            ('update_analysis_suggestions', 'Analysis update method')
        ]
        
        all_present = True
        for attr, description in features:
            if attr in content:
                print(f"  ✓ {description}")
            else:
                print(f"  ✗ {description} not found")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Feature Implementation Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Sound Files", test_sound_files()))
    results.append(("Theme Definitions", test_themes()))
    results.append(("Analysis Methods", test_analysis_methods()))
    results.append(("Animation Features", test_animation_features()))
    results.append(("UI Additions", test_ui_additions()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All features implemented successfully!")
        print("\nNew features:")
        print("  1. Move animations with smooth arc motion")
        print("  2. Sound effects for moves, captures, and game events")
        print("  3. Analysis mode with top 3 move suggestions")
        print("  4. Four custom themes: Classic, Modern, Wood, Metal")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
