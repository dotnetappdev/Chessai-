"""
3D Chess Board Widget using OpenGL
"""

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QVector3D
from PyQt5.QtMultimedia import QSound
from OpenGL.GL import *
from OpenGL.GLU import *
import chess
import math
import os


class ChessBoard3D(QOpenGLWidget):
    """3D Chess Board OpenGL Widget"""
    
    move_made = pyqtSignal(str)
    
    # Theme definitions
    THEMES = {
        'Classic': {
            'light_square': (0.94, 0.85, 0.71),
            'dark_square': (0.71, 0.53, 0.39),
            'white_piece': (0.93, 0.93, 0.93),
            'black_piece': (0.2, 0.2, 0.2),
            'border': (0.55, 0.27, 0.07),
            'background': (0.53, 0.81, 0.92)
        },
        'Modern': {
            'light_square': (0.96, 0.96, 0.96),
            'dark_square': (0.45, 0.45, 0.65),
            'white_piece': (0.95, 0.95, 0.95),
            'black_piece': (0.15, 0.15, 0.15),
            'border': (0.3, 0.3, 0.3),
            'background': (0.2, 0.2, 0.25)
        },
        'Wood': {
            'light_square': (0.85, 0.70, 0.50),
            'dark_square': (0.50, 0.35, 0.20),
            'white_piece': (0.95, 0.90, 0.80),
            'black_piece': (0.25, 0.15, 0.10),
            'border': (0.40, 0.25, 0.15),
            'background': (0.60, 0.50, 0.40)
        },
        'Metal': {
            'light_square': (0.80, 0.80, 0.85),
            'dark_square': (0.35, 0.35, 0.40),
            'white_piece': (0.90, 0.90, 0.95),
            'black_piece': (0.20, 0.20, 0.25),
            'border': (0.25, 0.25, 0.30),
            'background': (0.15, 0.15, 0.20)
        }
    }
    
    def __init__(self, board, parent=None):
        super().__init__(parent)
        self.board = board
        self.selected_square = None
        self.legal_moves_from_square = []
        
        # Camera settings
        self.camera_distance = 15.0
        self.camera_angle_x = 45.0
        self.camera_angle_y = 45.0
        
        # Mouse interaction
        self.last_mouse_pos = QPoint()
        
        # Animation settings
        self.animating = False
        self.animation_progress = 0.0
        self.animation_from = None
        self.animation_to = None
        self.animation_piece = None
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_duration = 300  # milliseconds
        
        # Theme settings
        self.current_theme = 'Classic'
        
        # Analysis mode
        self.analysis_mode = False
        self.suggested_moves = []
        
        # Sound effects
        self.sounds_enabled = True
        self.init_sounds()
        
        # Piece representations
        self.piece_unicode = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }
    
    def init_sounds(self):
        """Initialize sound effects"""
        self.sounds = {}
        sound_dir = 'sounds'
        
        # Create sound directory if it doesn't exist
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir)
        
        # Try to load sounds, but don't fail if they don't exist
        sound_files = {
            'move': 'move.wav',
            'capture': 'capture.wav',
            'check': 'check.wav',
            'checkmate': 'checkmate.wav'
        }
        
        for sound_type, filename in sound_files.items():
            filepath = os.path.join(sound_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[sound_type] = QSound(filepath)
                except:
                    pass
    
    def play_sound(self, sound_type):
        """Play a sound effect"""
        if self.sounds_enabled and sound_type in self.sounds:
            try:
                self.sounds[sound_type].play()
            except:
                pass
    
    def set_theme(self, theme_name):
        """Change the visual theme"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self.update()
    
    def get_theme_color(self, color_name):
        """Get a color from the current theme"""
        return self.THEMES[self.current_theme].get(color_name, (1.0, 1.0, 1.0))
    
    def set_analysis_mode(self, enabled):
        """Enable or disable analysis mode"""
        self.analysis_mode = enabled
        self.update()
    
    def set_suggested_moves(self, moves):
        """Set suggested moves for analysis mode"""
        self.suggested_moves = moves
        self.update()
    
    def animate_move(self, from_square, to_square, piece):
        """Start a move animation"""
        self.animating = True
        self.animation_progress = 0.0
        self.animation_from = from_square
        self.animation_to = to_square
        self.animation_piece = piece
        self.animation_timer.start(16)  # ~60 FPS
    
    def update_animation(self):
        """Update animation progress"""
        self.animation_progress += 16.0 / self.animation_duration
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animating = False
            self.animation_timer.stop()
            self.animation_from = None
            self.animation_to = None
            self.animation_piece = None
        
        self.update()
        
    def initializeGL(self):
        """Initialize OpenGL"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.4, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        
        # Background color from theme
        bg = self.get_theme_color('background')
        glClearColor(bg[0], bg[1], bg[2], 1.0)
        
    def resizeGL(self, w, h):
        """Handle resize"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h if h > 0 else 1, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        camera_x = self.camera_distance * math.cos(math.radians(self.camera_angle_x)) * math.cos(math.radians(self.camera_angle_y))
        camera_y = self.camera_distance * math.sin(math.radians(self.camera_angle_y))
        camera_z = self.camera_distance * math.sin(math.radians(self.camera_angle_x)) * math.cos(math.radians(self.camera_angle_y))
        
        gluLookAt(camera_x, camera_y, camera_z,  # Camera position
                  0.0, 0.0, 0.0,                  # Look at center
                  0.0, 1.0, 0.0)                  # Up vector
        
        # Draw board and pieces
        self.draw_board()
        self.draw_pieces()
        
    def draw_board(self):
        """Draw the chess board"""
        square_size = 1.0
        light_color = self.get_theme_color('light_square')
        dark_color = self.get_theme_color('dark_square')
        
        # Draw squares
        for rank in range(8):
            for file in range(8):
                is_light = (rank + file) % 2 == 0
                square = chess.square(file, rank)
                
                # Highlight selected square
                if self.selected_square and self.selected_square == square:
                    glColor3f(1.0, 1.0, 0.0)  # Yellow
                # Highlight legal move squares
                elif square in [chess.Move.from_uci(m).to_square for m in self.legal_moves_from_square]:
                    glColor3f(0.56, 0.93, 0.56)  # Light green
                # Highlight suggested moves in analysis mode
                elif self.analysis_mode and any(chess.Move.from_uci(m).to_square == square for m in self.suggested_moves):
                    glColor3f(0.56, 0.76, 0.93)  # Light blue
                # Normal squares
                elif is_light:
                    glColor3f(*light_color)
                else:
                    glColor3f(*dark_color)
                
                x = file - 3.5
                z = rank - 3.5
                
                glBegin(GL_QUADS)
                glNormal3f(0.0, 1.0, 0.0)
                glVertex3f(x, 0.0, z)
                glVertex3f(x + square_size, 0.0, z)
                glVertex3f(x + square_size, 0.0, z + square_size)
                glVertex3f(x, 0.0, z + square_size)
                glEnd()
        
        # Draw board border
        border_color = self.get_theme_color('border')
        glColor3f(*border_color)
        border_height = -0.2
        border_width = 0.3
        
        # Bottom border
        glBegin(GL_QUADS)
        for side in range(4):
            angle = side * 90
            glPushMatrix()
            glRotatef(angle, 0, 1, 0)
            glNormal3f(0.0, 1.0, 0.0)
            glVertex3f(-4.5, border_height, -4.5)
            glVertex3f(4.5, border_height, -4.5)
            glVertex3f(4.5, border_height, -4.5 - border_width)
            glVertex3f(-4.5, border_height, -4.5 - border_width)
            glPopMatrix()
        glEnd()
        
    def draw_pieces(self):
        """Draw chess pieces"""
        white_color = self.get_theme_color('white_piece')
        black_color = self.get_theme_color('black_piece')
        
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, rank)
                
                # Skip the piece being animated
                if self.animating and self.animation_from == square:
                    continue
                
                piece = self.board.piece_at(square)
                
                if piece:
                    x = file - 3.5
                    z = rank - 3.5
                    
                    glPushMatrix()
                    glTranslatef(x + 0.5, 0.0, z + 0.5)
                    
                    # Set piece color
                    if piece.color == chess.WHITE:
                        glColor3f(*white_color)
                    else:
                        glColor3f(*black_color)
                    
                    self.draw_piece(piece.piece_type)
                    glPopMatrix()
        
        # Draw animating piece
        if self.animating and self.animation_piece:
            from_file = chess.square_file(self.animation_from)
            from_rank = chess.square_rank(self.animation_from)
            to_file = chess.square_file(self.animation_to)
            to_rank = chess.square_rank(self.animation_to)
            
            # Interpolate position
            t = self.animation_progress
            # Use easing function for smoother animation
            t = t * t * (3.0 - 2.0 * t)  # Smoothstep
            
            x = (from_file + (to_file - from_file) * t) - 3.5
            z = (from_rank + (to_rank - from_rank) * t) - 3.5
            y = math.sin(t * math.pi) * 0.5  # Arc motion
            
            glPushMatrix()
            glTranslatef(x + 0.5, y, z + 0.5)
            
            # Set piece color
            if self.animation_piece.color == chess.WHITE:
                glColor3f(*white_color)
            else:
                glColor3f(*black_color)
            
            self.draw_piece(self.animation_piece.piece_type)
            glPopMatrix()
    
    def draw_piece(self, piece_type):
        """Draw a specific piece type"""
        # Base for all pieces
        self.draw_cylinder(0.3, 0.1, 20)
        
        glTranslatef(0.0, 0.1, 0.0)
        
        if piece_type == chess.PAWN:
            self.draw_sphere(0.2, 15, 15)
        elif piece_type == chess.KNIGHT:
            glRotatef(45, 0, 1, 0)
            self.draw_cone(0.25, 0.6, 10)
        elif piece_type == chess.BISHOP:
            self.draw_cone(0.2, 0.7, 20)
        elif piece_type == chess.ROOK:
            self.draw_cube(0.35, 0.6, 0.35)
        elif piece_type == chess.QUEEN:
            self.draw_cone(0.25, 0.8, 20)
            glTranslatef(0.0, 0.8, 0.0)
            self.draw_sphere(0.15, 10, 10)
        elif piece_type == chess.KING:
            self.draw_cone(0.25, 0.9, 20)
            glTranslatef(0.0, 0.9, 0.0)
            # Crown cross
            glPushMatrix()
            self.draw_cube(0.15, 0.05, 0.05)
            glRotatef(90, 0, 0, 1)
            self.draw_cube(0.15, 0.05, 0.05)
            glPopMatrix()
    
    def draw_sphere(self, radius, slices, stacks):
        """Draw a sphere"""
        sphere = gluNewQuadric()
        gluSphere(sphere, radius, slices, stacks)
        gluDeleteQuadric(sphere)
    
    def draw_cylinder(self, radius, height, slices):
        """Draw a cylinder"""
        cylinder = gluNewQuadric()
        gluCylinder(cylinder, radius, radius, height, slices, 1)
        gluDeleteQuadric(cylinder)
    
    def draw_cone(self, base_radius, height, slices):
        """Draw a cone"""
        cone = gluNewQuadric()
        gluCylinder(cone, base_radius, 0.0, height, slices, 1)
        gluDeleteQuadric(cone)
    
    def draw_cube(self, width, height, depth):
        """Draw a cube"""
        w, h, d = width / 2, height, depth / 2
        
        glBegin(GL_QUADS)
        # Front
        glNormal3f(0, 0, 1)
        glVertex3f(-w, 0, d)
        glVertex3f(w, 0, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)
        
        # Back
        glNormal3f(0, 0, -1)
        glVertex3f(-w, 0, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, 0, -d)
        
        # Left
        glNormal3f(-1, 0, 0)
        glVertex3f(-w, 0, -d)
        glVertex3f(-w, 0, d)
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)
        
        # Right
        glNormal3f(1, 0, 0)
        glVertex3f(w, 0, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, h, d)
        glVertex3f(w, 0, d)
        
        # Top
        glNormal3f(0, 1, 0)
        glVertex3f(-w, h, -d)
        glVertex3f(-w, h, d)
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)
        
        # Bottom
        glNormal3f(0, -1, 0)
        glVertex3f(-w, 0, -d)
        glVertex3f(w, 0, -d)
        glVertex3f(w, 0, d)
        glVertex3f(-w, 0, d)
        glEnd()
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            # Try to select a square
            square = self.get_square_from_mouse(event.x(), event.y())
            if square is not None:
                self.handle_square_click(square)
        
        self.last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for camera rotation"""
        if event.buttons() & Qt.RightButton:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            
            self.camera_angle_x += dx * 0.5
            self.camera_angle_y = max(-89, min(89, self.camera_angle_y + dy * 0.5))
            
            self.update()
        
        self.last_mouse_pos = event.pos()
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        self.camera_distance = max(5.0, min(30.0, self.camera_distance - delta / 120.0))
        self.update()
    
    def get_square_from_mouse(self, mouse_x, mouse_y):
        """Convert mouse coordinates to chess square"""
        # Get viewport and matrices
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # Convert mouse coordinates
        win_x = float(mouse_x)
        win_y = float(viewport[3] - mouse_y)
        
        # Read depth at mouse position
        glReadBuffer(GL_FRONT)
        win_z = glReadPixels(int(win_x), int(win_y), 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
        
        if win_z >= 1.0:
            return None
        
        try:
            # Unproject to world coordinates
            world_coords = gluUnProject(win_x, win_y, win_z, modelview, projection, viewport)
            
            # Convert world coordinates to board square
            file = int(world_coords[0] + 4.0)
            rank = int(world_coords[2] + 4.0)
            
            if 0 <= file < 8 and 0 <= rank < 8:
                return chess.square(file, rank)
        except:
            pass
        
        return None
    
    def handle_square_click(self, square):
        """Handle click on a square"""
        piece = self.board.piece_at(square)
        
        # If we have a selected square and this is a legal move
        if self.selected_square is not None:
            move_uci = chess.square_name(self.selected_square) + chess.square_name(square)
            
            # Check for pawn promotion
            selected_piece = self.board.piece_at(self.selected_square)
            if selected_piece and selected_piece.piece_type == chess.PAWN:
                to_rank = chess.square_rank(square)
                if (selected_piece.color == chess.WHITE and to_rank == 7) or \
                   (selected_piece.color == chess.BLACK and to_rank == 0):
                    move_uci += 'q'  # Auto-promote to queen
            
            # Try to make the move
            if move_uci in [m.uci() for m in self.board.legal_moves]:
                self.move_made.emit(move_uci)
                self.selected_square = None
                self.legal_moves_from_square = []
                self.update()
                return
        
        # Select a new piece
        if piece and piece.color == self.board.turn:
            self.selected_square = square
            
            # Get legal moves from this square
            self.legal_moves_from_square = [
                move.uci() for move in self.board.legal_moves
                if move.from_square == square
            ]
            
            self.update()
        else:
            # Deselect
            self.selected_square = None
            self.legal_moves_from_square = []
            self.update()
    
    def update_board(self, board, last_move=None):
        """Update the board state"""
        # Trigger animation if there was a move
        if last_move and not self.animating:
            try:
                move = chess.Move.from_uci(last_move) if isinstance(last_move, str) else last_move
                piece = self.board.piece_at(move.from_square)
                if piece:
                    # Determine if it's a capture
                    is_capture = self.board.piece_at(move.to_square) is not None
                    
                    # Update board first
                    self.board = board
                    
                    # Play sound
                    if self.board.is_checkmate():
                        self.play_sound('checkmate')
                    elif self.board.is_check():
                        self.play_sound('check')
                    elif is_capture:
                        self.play_sound('capture')
                    else:
                        self.play_sound('move')
                    
                    # Start animation
                    self.animate_move(move.from_square, move.to_square, piece)
                    return
            except:
                pass
        
        self.board = board
        self.selected_square = None
        self.legal_moves_from_square = []
        self.update()
