"""
3D Chess Board Widget using OpenGL
"""

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QVector3D
from OpenGL.GL import *
from OpenGL.GLU import *
import chess
import math


class ChessBoard3D(QOpenGLWidget):
    """3D Chess Board OpenGL Widget"""
    
    move_made = pyqtSignal(str)
    
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
        
        # Piece representations
        self.piece_unicode = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }
        
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
        
        # Background color
        glClearColor(0.53, 0.81, 0.92, 1.0)  # Sky blue
        
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
        
        # Draw squares
        for rank in range(8):
            for file in range(8):
                is_light = (rank + file) % 2 == 0
                
                # Highlight selected square
                if self.selected_square and self.selected_square == chess.square(file, rank):
                    glColor3f(1.0, 1.0, 0.0)  # Yellow
                # Highlight legal move squares
                elif chess.square(file, rank) in [chess.Move.from_uci(m).to_square for m in self.legal_moves_from_square]:
                    glColor3f(0.56, 0.93, 0.56)  # Light green
                # Normal squares
                elif is_light:
                    glColor3f(0.94, 0.85, 0.71)  # Light square
                else:
                    glColor3f(0.71, 0.53, 0.39)  # Dark square
                
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
        glColor3f(0.55, 0.27, 0.07)  # Brown
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
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                
                if piece:
                    x = file - 3.5
                    z = rank - 3.5
                    
                    glPushMatrix()
                    glTranslatef(x + 0.5, 0.0, z + 0.5)
                    
                    # Set piece color
                    if piece.color == chess.WHITE:
                        glColor3f(0.93, 0.93, 0.93)  # White
                    else:
                        glColor3f(0.2, 0.2, 0.2)  # Black
                    
                    self.draw_piece(piece.piece_type)
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
    
    def update_board(self, board):
        """Update the board state"""
        self.board = board
        self.selected_square = None
        self.legal_moves_from_square = []
        self.update()
