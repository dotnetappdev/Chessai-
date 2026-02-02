# 3D Chess AI

A sophisticated 3D chess game with AI capabilities that can learn and improve through self-play. Built with Python (Flask backend) and Three.js (3D visualization).

## Features

- **3D Chess Board**: Fully interactive 3D chess board with realistic piece models
- **AI Opponent**: Play against an AI that uses minimax algorithm with alpha-beta pruning
- **AI Learning**: Neural network-based evaluation that learns from games
- **Self-Play Mode**: Watch the AI play against itself to train and improve
- **Game Modes**:
  - Player vs AI
  - AI vs AI (self-play)
- **Save/Load Games**: Import and export games in PGN (Portable Game Notation) format
- **Model Persistence**: Save and load trained AI models
- **Interactive 3D Controls**: Rotate, zoom, and interact with the board

## Technology Stack

- **Backend**: Python with Flask
- **Chess Logic**: python-chess library
- **AI/ML**: TensorFlow/Keras for neural network
- **Frontend**: HTML5, CSS3, JavaScript
- **3D Visualization**: Three.js
- **Format Support**: PGN (Portable Game Notation)

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser with WebGL support

## Installation

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
   - Flask (web framework)
   - Flask-CORS (cross-origin support)
   - python-chess (chess logic and PGN support)
   - numpy (numerical computing)
   - tensorflow (machine learning)

## Usage

### Starting the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

### Playing the Game

#### Player vs AI Mode
1. Select "Player vs AI" from the mode dropdown
2. Click on a piece to see legal moves (highlighted in green)
3. Click on a highlighted square to make your move
4. The AI will automatically respond after your move

#### AI vs AI Mode (Self-Play)
1. Select "AI vs AI" from the mode dropdown
2. Click "Start Self-Play" to watch the AI play against itself
3. Click "Stop" to pause the self-play
4. This mode is useful for generating training data

### 3D Controls

- **Rotate**: Click and drag to rotate the camera around the board
- **Zoom**: Use mouse wheel to zoom in/out
- **Reset View**: Refresh the page to reset camera position

### Saving and Loading Games

#### Save a Game
1. Enter a filename (e.g., "mygame.pgn") or leave blank for auto-generated name
2. Click "Save Game"
3. Games are saved in PGN format in the `games/` directory

#### Load a Game
1. Select a game from the dropdown menu
2. Click "Load Game"
3. The board will update to show the loaded game position

### AI Training

The AI uses a neural network to evaluate chess positions and can improve through training.

#### Train the AI
1. Play some games or run self-play mode to generate training data
2. Click "Train AI (10 epochs)" to train the neural network
3. Training uses the positions encountered during play
4. The AI learns to evaluate positions better over time

#### Save/Load Model
- **Save Model**: Saves the trained neural network to `models/chess_ai.keras`
- **Load Model**: Loads a previously saved model
- Models persist between sessions, so your AI's learning is saved

## Project Structure

```
Chessai-/
├── app.py                 # Flask web server and API endpoints
├── chess_ai.py           # AI implementation with neural network
├── requirements.txt      # Python dependencies
├── static/
│   ├── index.html       # Main HTML page
│   └── chess3d.js       # 3D visualization and game logic
├── games/               # Saved games in PGN format (created on first save)
└── models/              # Saved AI models (created on first save)
```

## API Endpoints

The Flask backend provides the following REST API endpoints:

- `GET /api/board` - Get current board state
- `POST /api/move` - Make a move
- `POST /api/ai-move` - Get AI move
- `POST /api/reset` - Reset the board
- `GET /api/mode` - Get current game mode
- `POST /api/mode` - Set game mode
- `POST /api/self-play` - Make one self-play move
- `POST /api/save` - Save game to PGN
- `POST /api/load` - Load game from PGN
- `GET /api/games` - List saved games
- `POST /api/train` - Train AI model
- `POST /api/model/save` - Save AI model
- `POST /api/model/load` - Load AI model

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
- Import games from other chess software
- Export games for analysis in other tools
- Games include metadata (date, players, etc.)
- Full move history preserved

## Tips for Better AI Performance

1. **Generate Training Data**: Run self-play mode to generate diverse positions
2. **Train Regularly**: After significant games, train the AI to improve evaluation
3. **Save Models**: Don't forget to save after training to preserve improvements
4. **Multiple Training Sessions**: The AI improves incrementally with each training session

## Troubleshooting

### Server Won't Start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 5000 is available
- Try running with a different port: `flask run --port 5001`

### 3D Board Not Rendering
- Ensure your browser supports WebGL
- Try a different browser (Chrome, Firefox, Edge recommended)
- Check browser console for errors

### AI Moves Too Slowly
- The AI uses depth-2 search by default
- Lower depth for faster moves (edit `chess_ai.py`)
- Neural network predictions are fast; material evaluation is used as fallback

### Training Takes Too Long
- Reduce epochs (default is 10)
- Ensure you have enough training data from played games
- TensorFlow will use GPU if available for faster training

## Future Enhancements

Possible improvements for future versions:
- Adjustable AI difficulty levels
- Opening book integration
- Endgame tablebase support
- Online multiplayer support
- Move animations
- Sound effects
- Analysis mode with move suggestions
- Custom piece designs

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Acknowledgments

- **python-chess**: Excellent chess library by Niklas Fiekas
- **Three.js**: 3D graphics library
- **TensorFlow**: Machine learning framework
- **Flask**: Lightweight web framework