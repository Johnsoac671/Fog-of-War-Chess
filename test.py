from dark_chess import DarkChess
from engine.minichess.chess.fastchess_utils import visualize_board

bob = DarkChess()

move = bob.get_legal_moves()[3]
bob.action(move)

print(bob.visualize())
