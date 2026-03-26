from engine.game.dark_chess import Game
from engine.agents.agent import Agent

class AlphaBetaAgent(Agent):
    '''Chooses a move using alpha-beta pruning'''
    
    def __init__(self, name, color):
        self.name = name
        self.color = color
        
        self.alpha = float("-inf")
        self.beta = float("inf")
    
    def choose_move(self, game: Game):
        # list of moves in this format:
        # tuple(x pos of piece, y pos of piece, delta x of new location, delta y of new location, piece to promote to if applicable)
        moves = game.get_legal_moves()
    
    # given game returns max utility value
    def ALPHA_BETA_SEARCH(self, game: Game):
        v = self.max_value(game)
    
    # determines MAX_VALUE given inputs
    def MAX_VALUE(self, game, alpha=float('-inf'), beta=float('inf'), depth=0, max_depth=4):
        

# keeps track of total utility for each team
class 