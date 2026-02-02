# 3D Chess AI - Desktop Application

A sophisticated 3D chess game with AI capabilities that can learn and improve through self-play. Built as a **standalone desktop application** that runs locally without requiring a web browser or server.

## Features

- **3D Chess Board**: Fully interactive 3D chess board with realistic piece models using OpenGL
- **AI Opponent**: Play against an AI that uses minimax algorithm with alpha-beta pruning
- **AI Learning**: Neural network-based evaluation that learns from games
- **Pre-trained Model**: Comes with initial training data from famous grandmaster games
- **Automatic Training**: AI automatically improves after games
- **Flexible Training Modes**:
  - Train every game (ideal for self-play)
  - Train every 5 games (default for regular play)
- **Learn from Grandmaster Games**: Load PGN files from famous games to train the AI
- **Self-Play Mode**: Watch the AI play against itself to train and improve
- **Game Modes**:
  - Player vs AI
  - AI vs AI (self-play)
- **Save/Load Games**: Import and export games in PGN (Portable Game Notation) format
- **Model Persistence**: Save and load trained AI models
- **Interactive 3D Controls**: Rotate, zoom, and interact with the board
- **Standalone Executable**: Can be built into a single .exe with all dependencies included

## Technology Stack

- **GUI Framework**: PyQt5
- **3D Graphics**: PyOpenGL (OpenGL)
- **Chess Logic**: python-chess library
- **AI/ML**: TensorFlow/Keras for neural network
- **Packaging**: PyInstaller for creating standalone executables
- **Format Support**: PGN (Portable Game Notation)

## Requirements

### For Running from Source
- Python 3.8 or higher
- pip (Python package manager)
- OpenGL support (usually built into OS)

### For Running the Executable
- **Windows**: Windows 7 or later with OpenGL support
- **No Python installation required** when using the built executable

## Installation

### Option 1: Run from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dotnetappdev/Chessai-.git
   cd Chessai-
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - PyQt5 (GUI framework)
   - PyOpenGL (3D graphics)
   - python-chess (chess logic and PGN support)
   - numpy (numerical computing)
   - tensorflow (machine learning)
   - pyinstaller (for building executables)

3. **Run the application**:
   ```bash
   python main.py
   ```

### Option 2: Build Standalone Executable

1. **Install dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Build the executable**:
   ```bash
   pyinstaller ChessAI.spec
   ```

3. **Find the executable**:
   - The built application will be in the `dist/ChessAI/` directory
   - Run `ChessAI.exe` (Windows) or `ChessAI` (Linux/Mac)
   - **All DLLs and dependencies are included** in the dist folder
   - You can copy the entire `dist/ChessAI/` folder to any computer and run it

4. **Optional: Create a single-file executable**:
   ```bash
   pyinstaller --onefile --windowed main.py
   ```
   This creates a single .exe file (larger, slower startup, but easier to distribute)

## Usage

### Starting the Application

**From Source:**
```bash
python main.py
```

**From Executable:**
- Double-click `ChessAI.exe` in the `dist/ChessAI/` folder

### Playing the Game

#### Player vs AI Mode
1. Select "Player vs AI" from the mode dropdown (default)
2. Click on a piece to see legal moves (highlighted in green)
3. Click on a highlighted square to make your move
4. The AI will automatically respond after your move

#### AI vs AI Mode (Self-Play)
1. Select "AI vs AI" from the mode dropdown
2. Check "Train after each self-play game" to enable training after every game (recommended)
3. Click "Start Self-Play" to watch the AI play against itself
4. Click "Stop Self-Play" to pause
5. This mode is useful for generating training data and improving the AI quickly

### 3D Controls

- **Rotate Camera**: Right-click and drag to rotate the view around the board
- **Zoom**: Use mouse wheel to zoom in/out
- **Select Piece**: Left-click on a piece
- **Make Move**: Left-click on a legal move square (highlighted in green)

### Saving and Loading Games

#### Save a Game
1. Click "Save Game (PGN)" button
2. Choose a location and filename
3. Games are saved in standard PGN format

#### Load a Game
1. Click "Load Game (PGN)" button
2. Select a previously saved .pgn file
3. The board will update to show the loaded game position

### AI Training

The AI uses a neural network to evaluate chess positions and can improve through training.

#### Pre-trained Model
- The AI comes with initial training data from 173 positions extracted from famous grandmaster games
- This provides a solid starting point for the AI's learning
- To create a fully trained model with TensorFlow installed, run: `python pretrain_model.py`

#### Automatic Training
- **Regular Play**: AI trains after every 5 completed games
- **Self-Play Mode**: Enable "Train after each self-play game" checkbox to train after EVERY game
- Training uses positions encountered during play
- The model is automatically saved after training
- No manual intervention needed - just play!

#### Manual Training
1. Play some games or run self-play mode to generate training data
2. Click "Train AI (10 epochs)" to manually train the neural network
3. The training data counter shows how many positions are available
4. Training improves the AI's position evaluation

#### Learn from Grandmaster Games
1. Click "Learn from PGN File" button
2. Select a PGN file containing chess games (e.g., from Chess.com, Lichess, or famous game databases)
3. The AI will analyze all games in the file and learn from the positions
4. Each game adds dozens of training positions
5. Click "Train AI" after loading to apply the learning

**Where to get PGN files:**
- Use the included `example_games.pgn` (Fischer, Anderssen famous games)
- Download from Chess.com (your own games or master games)
- Export from Lichess (games database)
- Use chess game databases (e.g., Kasparov, Fischer, Carlsen games)
- Any standard PGN format file works

**Quick Start with Example Games:**
```bash
# The repository includes example_games.pgn with 3 famous games
# In the app, click "Learn from PGN File" and select example_games.pgn
# This will add ~90 positions to train from
```

#### Save/Load Model
- **Save Model**: Saves the trained neural network to `models/chess_ai.keras`
- **Load Model**: Loads a previously saved model
- Models persist between sessions, so your AI's learning is saved
- Auto-save happens after automatic training

## Project Structure

```
Chessai-/
├── main.py                     # Main application entry point
├── chess_ai.py                # AI implementation with neural network
├── chess_board_3d.py          # 3D OpenGL chess board widget
├── pretrain_model.py          # Script to pre-train the AI model
├── requirements.txt           # Python dependencies
├── ChessAI.spec              # PyInstaller build configuration
├── test_components.py        # Component testing
├── example_games.pgn         # Example grandmaster games for training
├── models/
│   └── initial_training_data.pkl  # Pre-loaded training data from example games
├── README.md                 # Complete documentation
├── QUICKSTART.md            # Quick start guide
├── BUILD_INSTRUCTIONS.md    # Building executables
└── PROJECT_SUMMARY.md       # Project overview
```

## Pre-Training the AI (Optional)

If you have TensorFlow installed, you can create a fully pre-trained model:

```bash
# Install TensorFlow (optional)
pip install tensorflow

# Run the pre-training script
python pretrain_model.py
```

This will:
1. Load positions from `example_games.pgn`
2. Train a neural network for 20 epochs
3. Save the trained model to `models/chess_ai.keras`

**Note**: The AI works without TensorFlow using classical evaluation. Pre-training is optional but recommended for better performance.
├── ChessAI.spec          # PyInstaller build configuration
├── build.py              # Build script helper
├── games/                # Saved games in PGN format (created on first save)
└── models/               # Saved AI models (created on first save)
```

## Building for Distribution

### Windows Executable

To create a distributable Windows executable:

```bash
# Install dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller ChessAI.spec

# The executable and all DLLs will be in dist/ChessAI/
# Distribute the entire dist/ChessAI/ folder
```

### What Gets Included

The built executable includes:
- ChessAI.exe (main executable)
- Python runtime
- PyQt5 DLLs
- OpenGL libraries
- TensorFlow libraries
- All other dependencies

**Total size**: Approximately 400-600 MB due to TensorFlow

### Reducing Size (Optional)

To reduce the size of the distribution:

1. Use TensorFlow Lite instead of full TensorFlow
2. Remove unnecessary TensorFlow backends
3. Use `--exclude-module` with PyInstaller for unused modules

## How the AI Works

### Chess Logic
- Uses the `python-chess` library for move generation, validation, and game rules
- Supports all chess rules including castling, en passant, and promotion

### AI Algorithm
1. **Search**: Minimax algorithm with alpha-beta pruning (depth 2 by default)
2. **Evaluation**: Combines material count and neural network evaluation
3. **Learning**: Neural network learns position evaluations from played games

### Neural Network Architecture
- **Input**: 8x8x12 tensor (board position with 12 piece types)
- **Layers**: 
  - 2 Conv2D layers (32 and 64 filters)
  - Dense layers with dropout
  - Output: Single value (position evaluation)
- **Training**: Mean Squared Error loss, Adam optimizer

## PGN Format Support

The application uses PGN (Portable Game Notation), the standard format for chess games:
- Import games from other chess software (ChessBase, Lichess, Chess.com, etc.)
- Export games for analysis in other tools
- Games include metadata (date, players, etc.)
- Full move history preserved

## Tips for Better AI Performance

1. **Generate Training Data**: Run self-play mode to generate diverse positions
2. **Train Regularly**: After significant games, train the AI to improve evaluation
3. **Save Models**: Don't forget to save after training to preserve improvements
4. **Multiple Training Sessions**: The AI improves incrementally with each training session

## Troubleshooting

### Application Won't Start (Source)
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)
- Verify OpenGL support: Most systems have this built-in

### Application Won't Start (Executable)
- Ensure you have OpenGL support (standard on Windows 7+)
- Run from command line to see error messages
- Check Windows Defender/Antivirus isn't blocking it

### 3D Board Not Rendering
- Update your graphics drivers
- Ensure OpenGL is supported on your system
- Try running with administrator privileges

### AI Moves Too Slowly
- The AI uses depth-2 search by default
- Lower depth for faster moves (edit `chess_ai.py`, line ~165)
- Neural network predictions are fast; material evaluation is used as fallback

### Training Takes Too Long
- Reduce epochs (default is 10)
- Ensure you have enough training data from played games
- TensorFlow will use GPU if available for faster training

### Build Errors with PyInstaller
- Ensure PyInstaller is installed: `pip install pyinstaller`
- Use the provided `ChessAI.spec` file
- Check that all imports work: `python main.py` first
- Some antivirus software may interfere with PyInstaller

## Performance Notes

- **Startup Time**: First launch may be slower (TensorFlow initialization)
- **Memory Usage**: ~200-400 MB (TensorFlow models)
- **CPU Usage**: Spikes during AI moves and training
- **GPU**: TensorFlow will use GPU if available (CUDA)

## System Requirements

### Minimum
- **OS**: Windows 7 / Linux / macOS 10.12+
- **RAM**: 2 GB
- **Disk**: 1 GB free space
- **Graphics**: OpenGL 2.0 support

### Recommended
- **OS**: Windows 10/11 / Modern Linux / macOS 11+
- **RAM**: 4 GB or more
- **Disk**: 2 GB free space
- **Graphics**: OpenGL 3.0+ support
- **CPU**: Multi-core processor for faster AI

## Future Enhancements

Possible improvements for future versions:
- Adjustable AI difficulty levels
- Opening book integration
- Endgame tablebase support
- Network multiplayer support (without web browser)
- Move animations
- Sound effects
- Analysis mode with move suggestions
- Custom piece designs and themes
- Installer/Setup wizard

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Acknowledgments

- **python-chess**: Excellent chess library by Niklas Fiekas
- **PyQt5**: Cross-platform GUI framework
- **PyOpenGL**: Python OpenGL bindings
- **TensorFlow**: Machine learning framework
- **PyInstaller**: Creating standalone executables