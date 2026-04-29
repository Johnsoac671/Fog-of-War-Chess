import random

from engine.game.dark_chess import Game
from engine.agents.agent import Agent


class RandomAgent(Agent):
    '''Chooses a move at random from the pool of legal moves'''
    
    def __init__(self, name, color):
        self.name = name
        self.color = color
    
    def choose_move(self, game: Game):
        moves = game.get_legal_moves()
        
        return random.choice(moves)

class SmartRandomAgent(Agent):
    '''Always takes a move that wins if avaliable, otherwise chooses a move at random from the pool of legal moves'''
    
    def __init__(self, name, color):
        self.name = name
        self.color = color
    
    def choose_move(self, game: Game):
        moves = game.get_legal_moves()
        
        for move in moves:
            clone = game.copy()
            clone.take_action(move)
            
            if clone.get_result() == self.color:
                return move
        
        return random.choice(moves)
    