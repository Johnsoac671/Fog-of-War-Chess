import random
from engine.game.dark_chess import Game
from engine.agents.agent import Agent
from engine.determinization.determinizer import Determinizer, RandomDeterminizer


class MonteCarloAgent(Agent):
    def __init__(self, name: str, color: str, iterations: int = 100):
        self.name = name
        self.color = color
        self.iterations = iterations
        self.determinizer: Determinizer = RandomDeterminizer()


    def choose_move(self, game: Game):
        moves = game.get_legal_moves()
        
        if len(moves) == 1:
            return moves[0]

        scores = {x: 0.0 for x in range(len(moves))}
        

        sim_game = game.copy() 

        for _ in range(self.iterations):
            det_game = self.determinizer.determinize_board(game)

            for idx, move in enumerate(moves):
                
                det_game.copy_into(sim_game)
                
                sim_game.take_action(move)

                result = self.simulate_game(sim_game)
                scores[idx] += self.score_outcome(result)

        best_idx = max(scores, key=lambda x: scores[x])
        return moves[best_idx]


    def simulate_game(self, game: Game) -> str:
        MAX_LENGTH = 200

        for _ in range(MAX_LENGTH):
            result = game.get_result()
            
            if result is not None:
                return result

            moves = game.get_legal_moves()
            
            if not moves:
                return "D"

            game.take_action(random.choice(moves))

        return "D"


    def score_outcome(self, result: str) -> float:
        if result == self.color:
            return 1.0
        
        if result == "D":
            return 0.5
        
        return 0.0