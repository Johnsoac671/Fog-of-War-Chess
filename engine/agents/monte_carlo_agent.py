from engine.game.dark_chess import Game
from engine.agents.agent import Agent

class MonteCarloAgent(Agent):
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.iterations = 100
        
    def choose_move(self, game: Game):
        # determinize
        # for each move, play it then simulate 100 randomly played games
        # return the move that won the most
        pass