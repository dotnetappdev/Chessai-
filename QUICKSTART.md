# Quick Start Guide - 3D Chess AI Desktop Application

## For End Users (Running the Executable)

### Windows

1. Download the `ChessAI` folder containing `ChessAI.exe`
2. Double-click `ChessAI.exe` to launch
3. That's it! No installation needed.

**Note**: The first launch may take a few seconds to initialize.

### System Requirements
- Windows 7 or later
- OpenGL 2.0+ support (standard on most systems)
- 2 GB RAM minimum
- 1 GB free disk space

## For Developers (Running from Source)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/dotnetappdev/Chessai-.git
cd Chessai-

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Building the Executable

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build using the spec file
pyinstaller ChessAI.spec

# The executable will be in: dist/ChessAI/ChessAI.exe
```

## How to Play

### Controls
- **Left-click on a piece**: Select it (legal moves show in green)
- **Left-click on green square**: Make the move
- **Right-click and drag**: Rotate the camera
- **Mouse wheel**: Zoom in/out

### Game Modes
1. **Player vs AI** (default): You play White, AI plays Black
2. **AI vs AI**: Watch the AI play itself for training

### Key Features
- **New Game**: Start fresh
- **AI Move**: Force AI to move (in Player vs AI mode)
- **Self-Play**: AI plays both sides automatically
- **Save/Load**: Games saved in standard PGN format
- **AI Training**: Improve the AI by training on played games

## Troubleshooting

### Application won't start
- Ensure you have OpenGL support
- Try running from command line to see errors
- Check antivirus isn't blocking the executable

### Performance issues
- Lower window size
- Close other applications
- Check CPU usage during AI thinking

### 3D rendering issues
- Update graphics drivers
- Ensure OpenGL is enabled
- Try running with administrator privileges

## Building for Different Platforms

### Windows
```bash
pyinstaller ChessAI.spec
```

### Linux
```bash
pyinstaller ChessAI.spec
# Output will be: dist/ChessAI/ChessAI (no .exe extension)
```

### macOS
```bash
pyinstaller ChessAI.spec
# Output will be: dist/ChessAI/ChessAI.app
```

## Optional: TensorFlow for AI Learning

For AI training features, install TensorFlow:

```bash
pip install tensorflow
```

**Note**: TensorFlow is large (~400MB) and optional. The AI works without it using classical chess evaluation.

## Distribution

To distribute your built application:

1. Copy the entire `dist/ChessAI/` folder
2. Share the folder with users
3. Users run `ChessAI.exe` directly
4. All dependencies are included

**Total size**: ~50-100 MB without TensorFlow, ~400-600 MB with TensorFlow

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/dotnetappdev/Chessai-/issues
- Documentation: See README.md
