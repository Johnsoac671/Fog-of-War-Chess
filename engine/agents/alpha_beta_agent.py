import random

from engine.game.dark_chess import Game
from engine.agents.agent import Agent
from engine.determinization.determinizer import Determinizer, IgnoranceIsBlissDeterminizer

class AlphaBetaAgent(Agent):
    
    def __init__(self, name, color, max_depth=4, determinizer=IgnoranceIsBlissDeterminizer()):
        self.name = name
        self.color = color
        self.max_depth = max_depth
        # utility functions
        self.piece_values = {0: 1, 1: 3, 2: 3, 3: 5, 4: 9, 5: 1000}
        self.determinizer: Determinizer = determinizer

    def choose_move(self, game: Game):
        # assume fog is fully empty
        determinized_state = self.determinizer.determinize_board(game, self.color)
        return self.ALPHA_BETA_SEARCH(determinized_state)

    # from slide 34
    # returns best move given game
    def ALPHA_BETA_SEARCH(self, game: Game):
        best_value = float("-inf")
        best_move = None
        alpha = float("-inf")
        beta = float("inf")
        
        moves = game.get_legal_moves()
        if not moves:
            return None
            
        random.shuffle(moves) 
        
        for move in moves:
            result_state = game.copy()
            result_state.take_action(move)

            value = self.MIN_VALUE(result_state, alpha, beta, 1)
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)
            
        return best_move

    # slide 35: returns utility value
    def MAX_VALUE(self, game, alpha, beta, depth):
        # base case: end of game or reached depth limit
        if game.get_result() is not None or depth >= self.max_depth:
            return self.UTILITY(game)
        v = float("-inf")
        for move in game.get_legal_moves():
            result_state = game.copy()
            result_state.take_action(move)
            v = max(v, self.MIN_VALUE(result_state, alpha, beta, depth + 1))
            if v >= beta:
                # prune
                return v
            alpha = max(alpha, v)
        return v

    # slide 39: returns utility value
    def MIN_VALUE(self, game, alpha, beta, depth):
        # base case: end of game or reached depth limit
        if game.get_result() is not None or depth >= self.max_depth:
            return self.UTILITY(game)
        v = float("inf")
        for move in game.get_legal_moves():
            result_state = game.copy()
            result_state.take_action(move)
            v = min(v, self.MAX_VALUE(result_state, alpha, beta, depth + 1))
            if v <= alpha:
                # prune
                return v
            beta = min(beta, v)
        return v

    # calculates utility value of a state
    # for this agent's color
    def UTILITY(self, game: Game):
        score = 0
        board = game.board
        for color_idx in [0, 1]:
            color_str = "W" if color_idx == 1 else "B"
            # count pieces on each side and add or subtract \
            # depending on agent's color
            for piece_type in range(6):
                # count bits (pieces) on the bitboard
                count = bin(board.bitboards[color_idx, piece_type]).count('1')
                value = count * self.piece_values[piece_type]
                if color_str == self.color:
                    score += value
                else:
                    score -= value
        return score
