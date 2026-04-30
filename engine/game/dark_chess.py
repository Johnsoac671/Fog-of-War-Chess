from engine.game.minichess.util.chess_helpers import get_initial_chess_object
from engine.game.minichess.chess.fastchess_utils import piece_matrix_to_legal_moves, visualize_board

class Game():
    def __init__(self, variant="5x5gardner", client_side=None):
        self.board = get_initial_chess_object(variant)
        self.variant = variant
        self.current_player = "W"
        self.client_side = client_side
    
    def get_legal_moves(self):
        '''
        returns a list of all valid moves for the current player
        '''
        return piece_matrix_to_legal_moves(*self.board.legal_moves())
    
    
    def take_action(self, move) -> bool:
        '''
        performs a move, which can be directly passed from get_legal_moves()
        
        format: tuple(x pos of piece, y pos of piece, delta x of new location, delta y of new location, piece to promote to if applicable)
        '''
        (i, j), (dx, dy), promotion = move
        self.board.make_move(i, j, dx, dy, promotion)
        self._swap_player()
        
    def _swap_player(self):
        self.current_player = "W" if self.current_player == "B" else "B"
    
    def get_board_state(self, get_client=False):
        '''
        returns the visible squares for the current player (as a uint64 bitboard)
        '''
        # if get_client, we get the client's turn
        turn = self.board.turn if not get_client else self.client_side
        attacking_squares = self.board.get_attacked_squares(turn)
        active_pieces = self.board.get_all_pieces(False, [turn])
        
        return attacking_squares | active_pieces
    
    def copy(self):
        clone = Game(self.variant)
        clone.board = self.board.copy()
        clone.variant = self.variant
        clone.current_player = self.current_player
        
        return clone

    def copy_into(self, target):
        self.board.copy_into(target.board)
        target.variant = self.variant
        target.current_player = self.current_player

    def get_result(self):
        result = self.board.game_result() 
        if result == 1:
            return "W"
        elif result == -1:
            return "B"
        elif result == 0:
            return "D"
        # None, aka game is still going.
        return None
    
    def reset(self):
        self.board = get_initial_chess_object(self.variant)
        self.current_player = "W"
        
    def visualize(self, debug=False):
        
        if debug:
            visualize_board(self.board.bitboards, self.board.dims)
            return
            
        visible = self.get_board_state()
        
        masked_bitboards = self.board.bitboards.copy()

        enemy = 1 - self.board.turn
        
        for piece_type in range(6):
            masked_bitboards[enemy, piece_type] &= visible
        
        visualize_board(masked_bitboards, self.board.dims)
    
    # get visualization for the client
    def get_frontend_visualization(self):
        visible = self.get_board_state(True)
        masked_bitboards = self.board.bitboards.copy()
        enemy = 1 - self.client_side
        for piece_type in range(6):
            masked_bitboards[enemy, piece_type] &= visible
        return visualize_board(masked_bitboards, self.board.dims, True, visible)
    