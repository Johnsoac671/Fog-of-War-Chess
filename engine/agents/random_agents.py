import random

from engine.game.dark_chess import Game
from agent import Agent


class RandomAgent(Agent):
    def __init__(self, name):
        self.name = name
    
    def choose_move(self, game: Game):
        moves = game.get_legal_moves()
        
        return random.choice(moves)