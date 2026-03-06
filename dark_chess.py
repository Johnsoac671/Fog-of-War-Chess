from engine.minichess.util.chess_helpers import get_initial_chess_object
from engine.minichess.chess.fastchess_utils import piece_matrix_to_legal_moves

class DarkChess():
    def __init__(self, variant="5x5gardner"):
        self.board = get_initial_chess_object(variant)
    
    def get_legal_moves(self):
        '''
        returns a list of all valid moves for the current player
        '''
        return piece_matrix_to_legal_moves(*self.board.legal_moves())
    
    
    def action(self, move) -> bool:
        '''
        performs a move, which can be directly passed from get_legal_moves()
        
        format: tuple(x pos of piece, y pos of piece, delta x of new location, delta y of new location, piece to promote to if applicable)
        '''
        i, j, dx, dy, promotion = move
        self.board.make_move(i, j, dx, dy, promotion)
        
        return self.board.game_result is not None
    
    def get_board_state(self):
        '''
        returns the visible squares for the current player (as a uint64 bitboard)
        '''
        attacking_squares = self.board.get_attacked_squares(self.board.turn)
        active_pieces = self.board.get_all_pieces(False, [self.board.turn])
        
        return attacking_squares | active_pieces