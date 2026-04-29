import numpy as np
from engine.game.dark_chess import Game
from engine.game.minichess.chess.fastchess_utils import has_bit, flat

def get_move_index(move):
    """Converts a move tuple into its index in the list of all 625 possible moves"""
    (i, j), (dx, dy), _ = move
    
    from_square = i * 5 + j
    to_square = (i + dx) * 5 + (j + dy)
    
    return from_square * 25 + to_square

def board_to_numpy(game: Game):
    """Converts the visible board into a 14x5x5 Tensor."""
    dims = game.board.dims
    array = np.zeros((14, dims[0], dims[1]), dtype=np.float32)
    
    visible_mask = game.get_board_state()
    
    for row in range(dims[0]):
        for col in range(dims[1]):
            f_idx = flat(row, col, dims)
            
            if has_bit(visible_mask, f_idx):
                piece_idx, color = game.board.any_piece_at(row, col)
                
                if piece_idx != -1:
                    layer = piece_idx if color == 1 else piece_idx + 6
                    array[layer, row, col] = 1
                    
            array[12, row, col] = 1
                
    if game.current_player == "W":
        array[13, :, :] = 1.0
        
    return array