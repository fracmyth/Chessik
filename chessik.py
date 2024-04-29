import pygame
from pygame.locals import *
import chess
import chess.engine
import math
import tkinter as tk
from tkinter import simpledialog
import os
# Define constants for the screen width and height
SCREEN_WIDTH = 850  # Increased width to accommodate the evaluation bar
SCREEN_HEIGHT = 850
NAVBAR_HEIGHT = 50

# Define constants for the board and square size
BOARD_SIZE = 8
SQUARE_SIZE = 800 // BOARD_SIZE

# Define the colors
WHITE = (255, 255, 255)
O = (255, 87, 51)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RO = (61, 230, 223)
# Define colors for the navbar
NAVBAR_COLOR = (200, 200, 200)
NAVBAR_TEXT_COLOR = BLACK
# Dictionary to map piece names to their respective image paths
PIECE_IMAGES = {
    'bK': 'images/bK.png', 'bQ': 'images/bQ.png', 'bR': 'images/bR.png',
    'bB': 'images/bB.png', 'bN': 'images/bN.png', 'bP': 'images/bP.png',
    'wK': 'images/wK.png', 'wQ': 'images/wQ.png', 'wR': 'images/wR.png',
    'wB': 'images/wB.png', 'wN': 'images/wN.png', 'wP': 'images/wP.png'
}

# Define mappings for screen coordinates to algebraic notation
FILE_MAP = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
RANK_MAP = {0: '1', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7', 7: '8'}

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chessik")
icon_image = pygame.image.load("images/wK.png")  # Replace "icon.png" with the path to your icon image
pygame.display.set_icon(icon_image)
# Load and resize piece images
piece_images = {}
for name, path in PIECE_IMAGES.items():
    piece_image = pygame.image.load(path)
    piece_image = pygame.transform.scale(piece_image, (SQUARE_SIZE, SQUARE_SIZE))
    piece_images[name] = piece_image

# Initialize Stockfish engine
with open("engine.txt", "r") as f:
    engine = chess.engine.SimpleEngine.popen_uci(f"engines/{f.read()}")
    se = f.read()
# Function to draw the hessboard
def draw_board():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = WHITE if (row + col) % 2 == 0 else O
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE + NAVBAR_HEIGHT, SQUARE_SIZE, SQUARE_SIZE))

# Function to draw the pieces on the board
def draw_pieces(board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            if piece:
                piece_name = piece.symbol().upper()
                if piece.color == chess.BLACK:
                    piece_name = 'b' + piece_name
                else:
                    piece_name = 'w' + piece_name
                piece_image = piece_images[piece_name]
                screen.blit(piece_image, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE + NAVBAR_HEIGHT, SQUARE_SIZE, SQUARE_SIZE))

# Function to convert screen coordinates to algebraic notation
def screen_to_algebraic(x, y):
    file_index = x // SQUARE_SIZE
    rank_index = 7 - ((y - NAVBAR_HEIGHT) // SQUARE_SIZE)
    try:
        file_letter = FILE_MAP[file_index]
    except:
        pass
    try:
        rank_number = RANK_MAP[rank_index]
    except:
        pass
    try:
        return file_letter + rank_number
    except:
        return "no"

# Function to update the board based on algebraic notation
def update_board(board, move):
    try:
        uci = chess.Move.from_uci(move)
        board.push(uci)
    except:
        pass

# Function to handle pawn promotion
def promote_pawn(board, square):
    # Show options for promotion
    promotion_options = ['q', 'r', 'n', 'b']  # Queen, rook, knight, bishop
    promotion_piece = promotion_options[0]  # Default to queen
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    promotion_piece = 'q'
                    running = False
                elif event.key == pygame.K_r:
                    promotion_piece = 'r'
                    running = False
                elif event.key == pygame.K_n:
                    promotion_piece = 'n'
                    running = False
                elif event.key == pygame.K_b:
                    promotion_piece = 'b'
                    running = False
    
    # Promote the pawn
    pawn_color = 'w' if board.turn == chess.WHITE else 'b'
    promotion_square = square
    if pawn_color == 'w':
        promotion_square -= 8  # Move back one rank for white
    else:
        promotion_square += 8  # Move forward one rank for black
    promotion_square = chess.square_file(promotion_square) + 1
    promotion_square = FILE_MAP[promotion_square] + RANK_MAP[7 - chess.square_rank(promotion_square)]
    move = chess.Move.from_uci(f"{chess.SQUARE_NAMES[square]}{promotion_square}{promotion_piece}")
    board.push(move)

# Function to draw an arrow indicating the best move
def draw_arrow(start_pos, end_pos):
    pygame.draw.line(screen, BLUE, start_pos, end_pos, 5)  # Main line of the arrow

    # Calculate positions for the arrowhead
    angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
    arrow_length = 15
    arrow_angle = math.pi / 6  # Angle of arrowhead
    arrowhead1 = (end_pos[0] - arrow_length * math.cos(angle - arrow_angle), end_pos[1] - arrow_length * math.sin(angle - arrow_angle))
    arrowhead2 = (end_pos[0] - arrow_length * math.cos(angle + arrow_angle), end_pos[1] - arrow_length * math.sin(angle + arrow_angle))

    # Draw arrowhead
    pygame.draw.line(screen, BLUE, end_pos, arrowhead1, 5)
    pygame.draw.line(screen, BLUE, end_pos, arrowhead2, 5)

# Function to draw the evaluation bar
def draw_evaluation_bar(score):
    bar_width = 50
    max_bar_height = SCREEN_HEIGHT - NAVBAR_HEIGHT * 2
    score_int = score/100

    # Determine bar height for white and black based on score magnitude
    if score_int >= 0:
        white_bar_height = max_bar_height/2+max_bar_height/20*score_int
        black_bar_height = max_bar_height-white_bar_height
    else:
        black_bar_height = max_bar_height/2+max_bar_height/20*abs(score_int)
        white_bar_height = max_bar_height-black_bar_height
    # Draw white evaluation bar at the bottom
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(SCREEN_WIDTH - bar_width, SCREEN_HEIGHT - NAVBAR_HEIGHT - white_bar_height, bar_width, white_bar_height))
    # Draw black evaluation bar at the top
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(SCREEN_WIDTH - bar_width, NAVBAR_HEIGHT, bar_width, black_bar_height))

# Function to save the game state to a file
def save_game(board):
    with open("saved_game.txt", "w") as file:
        file.write(board.fen())

# Function to load the game state from a file
def load_game(fen):
    return chess.Board(fen)

# Function to display a message box to enter FEN
def display_fen_input():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    fen_input = simpledialog.askstring("FEN Input", "Enter FEN string to load position:")
    if fen_input:
        return fen_input.strip()
    else:
        return None
def display_engine_input():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    engines = [f for f in os.listdir("engines")]
    fen_input = simpledialog.askstring("Engine Input", f"Available:\n{engines}")
    if fen_input:
        return fen_input.strip()
    else:
        return None

# Add variables to track selected piece, valid moves, and selected piece position
selected_piece = None
valid_moves = []
selected_piece_x = 0
selected_piece_y = 0

# Cache evaluation score and best move
evaluation_score = None
best_move = None

# Main loop
chess_board = chess.Board()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            x, y = event.pos
            if y < NAVBAR_HEIGHT:
                # Handle navbar click
                pass
            else:
                try:
                    algebraic_notation = screen_to_algebraic(x, y)
                    square = chess.parse_square(algebraic_notation)
                    piece = chess_board.piece_at(square)
                except:
                    pass
                if piece and piece.color == chess_board.turn:
                    selected_piece = square
                    valid_moves = [(move.from_square, move.to_square) for move in chess_board.legal_moves if move.from_square == square]
                    # Calculate the offset from the top-left corner of the selected piece
                    drag_offset_x = x - (chess.square_file(selected_piece) * SQUARE_SIZE)
                    drag_offset_y = y - ((7 - chess.square_rank(selected_piece)) * SQUARE_SIZE + NAVBAR_HEIGHT)
                elif selected_piece and square in valid_moves:
                    move = chess.Move(selected_piece, square)
                    if move in chess_board.legal_moves:
                        if chess.square_rank(square) == 0 or chess.square_rank(square) == 7:
                            if chess_board.piece_at(selected_piece).symbol().lower() == 'p':
                                promote_pawn(chess_board, square)
                            else:
                                update_board(chess_board, move.uci())
                        else:
                            update_board(chess_board, move.uci())
                        selected_piece = None
                        valid_moves.clear()  # Clear selection after move
                        # Reanalyze position after move
                        result = engine.analyse(chess_board, chess.engine.Limit(time=0.1))
                        evaluation_score = int(result["score"].relative.score())
                        if chess_board.turn == False:
                            evaluation_score  *= -1

                        best_move = result["pv"][0] if len(result["pv"]) > 0 else None
                else:
                    selected_piece = None
                    valid_moves.clear()
        elif event.type == pygame.MOUSEMOTION and selected_piece is not None:
            # Update the position of the selected piece while dragging
            x, y = event.pos
            selected_piece_x = x - drag_offset_x
            selected_piece_y = y - drag_offset_y
            selected_piece_x = max(0, min(selected_piece_x, SCREEN_WIDTH - SQUARE_SIZE))
            selected_piece_y = max(NAVBAR_HEIGHT, min(selected_piece_y, SCREEN_HEIGHT - SQUARE_SIZE))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left mouse button released
            if selected_piece is not None:
                # Snap the piece to the center of the square when released
                x, y = event.pos
                try:
                    new_square = chess.parse_square(screen_to_algebraic(x - drag_offset_x + SQUARE_SIZE // 2, y - drag_offset_y + SQUARE_SIZE // 2))
                    move = chess.Move(selected_piece, new_square)
                    if move in chess_board.legal_moves:
                        update_board(chess_board, move.uci())  # Update the board here
                        selected_piece = None
                        valid_moves.clear()
                        # Reanalyze position after move
                        result = engine.analyse(chess_board, chess.engine.Limit(time=0.1))
                        evaluation_score =int(result["score"].relative.score())
                        if chess_board.turn == False:
                            evaluation_score  *= -1
                        best_move = result["pv"][0] if len(result["pv"]) > 0 else None
                except:
                    pass
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                # Load the game when 'l' key is pressed
                fen_input = display_fen_input()
                if fen_input:
                    chess_board = load_game(fen_input.strip())
            if event.key == pygame.K_e:
                engine_input = display_engine_input()
                if engine_input:
                    with open('engine.txt','w') as f:
                        f.write(engine_input)
                    se = engine_input
                    engine = chess.engine.SimpleEngine.popen_uci(f"engines/{engine_input}")

    screen.fill(WHITE)
    # Draw navbar
    pygame.draw.rect(screen, NAVBAR_COLOR, pygame.Rect(0, 0, SCREEN_WIDTH, NAVBAR_HEIGHT))
    font = pygame.font.Font(None, 37)
    load_text = font.render("Load Position(press 'l')", True, NAVBAR_TEXT_COLOR)
    engine_text = font.render("Select Engine(press 'e')", True, NAVBAR_TEXT_COLOR)
    sengine_text = font.render(se, True, NAVBAR_TEXT_COLOR)
    screen.blit(load_text, (17, 10))
    screen.blit(engine_text, (307, 10))
    screen.blit(sengine_text, (607, 10))
    draw_board()
    draw_pieces(chess_board)

    if selected_piece is not None:
        pygame.draw.rect(screen, BLUE, pygame.Rect(selected_piece_x, selected_piece_y, SQUARE_SIZE, SQUARE_SIZE), 4)
        piece_name = chess_board.piece_at(selected_piece).symbol()
        piece_name = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()

        # Draw the selected piece at the current mouse position
        piece_image = piece_images[piece_name]
        screen.blit(piece_image, (selected_piece_x, selected_piece_y))

    # Draw arrow indicating best move
    if best_move is not None:
        start_pos = (chess.square_file(best_move.from_square) * SQUARE_SIZE + SQUARE_SIZE // 2, (7 - chess.square_rank(best_move.from_square)) * SQUARE_SIZE + SQUARE_SIZE // 2 + NAVBAR_HEIGHT)
        end_pos = (chess.square_file(best_move.to_square) * SQUARE_SIZE + SQUARE_SIZE // 2, (7 - chess.square_rank(best_move.to_square)) * SQUARE_SIZE + SQUARE_SIZE // 2 + NAVBAR_HEIGHT)
        draw_arrow(start_pos, end_pos)

    # Draw evaluation score
    if evaluation_score is not None:
        font = pygame.font.Font(None, 36)
        if evaluation_score>=0:
            evaluation_text = font.render("Evaluation: +" + str(evaluation_score/100), True, RO)
        else:
            evaluation_text = font.render("Evaluation: " + str(evaluation_score/100), True, RO)
        screen.blit(evaluation_text, (10, NAVBAR_HEIGHT))

    # Draw evaluation bar
    if evaluation_score is not None:
        draw_evaluation_bar(evaluation_score)

    pygame.display.flip()

# Quit Pygame
pygame.quit()
