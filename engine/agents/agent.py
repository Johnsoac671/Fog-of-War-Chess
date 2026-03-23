from abc import ABC, abstractmethod

from engine.game.dark_chess import Game

class Agent(ABC):
    
    @abstractmethod
    def choose_move(self, game: Game):
        pass