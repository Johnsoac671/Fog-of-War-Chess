from abc import ABC, abstractmethod
from engine.game.dark_chess import Game

class Determinizer(ABC):
    
    @abstractmethod
    def determinize_board(game: Game) -> Game:
        pass