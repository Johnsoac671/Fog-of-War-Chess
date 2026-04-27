import numpy as np
import random
from abc import ABC, abstractmethod
import torch

from engine.game.dark_chess import Game
from engine.game.minichess.chess.fastchess_utils import true_bits, unflat, B_1, flat, has_bit
from engine.util.util import board_to_numpy
from network_training import BeliefNetwork


class Determinizer(ABC):

    @abstractmethod
    def determinize_board(self, game: Game, color: str) -> Game:
        # game with fog -> game without fog
        pass

class IgnoranceIsBlissDeterminizer(Determinizer):
    """
    Just assumes all unseen spaces are empty
    """
    def __init__(self):
        self.state = Game()
        
    def determinize_board(self, game: Game, color: str) -> Game:
        visible_mask = game.get_board_state()
        hallucination = game.copy()
        enemy_idx = 0 if color == "W" else 1 # 0 is black
        
        for piece_type in range(6):
            hallucination.board.bitboards[enemy_idx, piece_type] &= visible_mask
            
        return hallucination

class BadDeterminizer(Determinizer):
    """
    Just assumes all unseen spaces are empty (except for the opposing king, who is assumed to be on a random unseen space if not visible)
    """
    def __init__(self):
        self.state = Game()
    
    def determinize_board(self, game: Game) -> Game:
        game.copy_into(self.state)

        board = self.state.board 
        dims = board.dims
        
        visible = game.get_board_state()
        enemy = 1 - board.turn
        
        for piece_type in range(6): 
            hidden_enemy = board.bitboards[enemy, piece_type] & ~visible
            
            for bit in true_bits(hidden_enemy):
                i, j = unflat(bit, dims)
                board.piece_lookup[enemy, i, j] = -1
                
            board.bitboards[enemy, piece_type] &= visible

        if board.bitboards[enemy, 5] == 0:
            
            all_squares = np.uint64(0)
            for r in range(dims[0]):
                for c in range(dims[1]):
                    all_squares |= (B_1 << np.uint64(8 * r + c))
                    
            hidden_mask = ~visible & all_squares
            candidate_bits = list(true_bits(hidden_mask))
            
            if candidate_bits:
                new_king_bit = int(random.choice(candidate_bits))
                ni, nj = unflat(new_king_bit, dims)
                
                board.bitboards[enemy, 5] |= (B_1 << np.uint64(new_king_bit))
                board.piece_lookup[enemy, ni, nj] = 5

        board.legal_move_cache = None
        board.promotion_move_cache = None
        
        return self.state

class CheatingDeterminizer(Determinizer):
    '''
    Just reveals all squares, basically makes the game regular chess
    '''
    def __init__(self):
        self.state = Game()
    
    def determinize_board(self, game: Game, color: str= None) -> Game:
        game.copy_into(self.state)
        return self.state


class RandomDeterminizer(Determinizer):
    """
    Randomly places the opponent's hidden pieces onto space
    that are not currently visible to the active player.
    """
    
    def __init__(self):
        self.state = Game()
    
    def determinize_board(self, game: Game, color: str) -> Game:
        game.copy_into(self.state)
        board = self.state.board
        dims = board.dims
        
        B_1 = np.uint64(1)

        visible = game.get_board_state()

        my_pieces = board.get_all_pieces(False, [board.turn])

        # the engine uses an internal 8x8 board, so we need to do some gross padding lol
        all_squares = np.uint64(0)
        for r in range(dims[0]):
            for c in range(dims[1]):
                all_squares |= (B_1 << np.uint64(8 * r + c))

        hidden_mask = ~visible & ~my_pieces & all_squares

        candidate_bits = list(true_bits(hidden_mask))
        if not candidate_bits:
            return self.state

        enemy = 1 - board.turn

        for piece_type in range(6):
            hidden_enemy = board.bitboards[enemy, piece_type] & ~visible

            for bit in true_bits(hidden_enemy):
                i, j = unflat(bit, dims)

                # Remove from real location
                board.bitboards[enemy, piece_type] &= ~(B_1 << np.uint64(bit))
                board.piece_lookup[enemy, i, j] = -1

                # Pick a free hidden square
                occupied_now = board.get_all_pieces(False)
                free = [
                    b for b in candidate_bits
                    if not (occupied_now >> np.uint64(b)) & B_1
                ]

                new_bit = int(np.random.choice(free))

                ni, nj = unflat(new_bit, dims)

                board.bitboards[enemy, piece_type] |= B_1 << np.uint64(new_bit)
                board.piece_lookup[enemy, ni, nj] = piece_type

        # recompute move cache with "new" positions
        board.legal_move_cache = None
        board.promotion_move_cache = None

        return self.state