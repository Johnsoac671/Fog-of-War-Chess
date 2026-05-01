import random
import math

from engine.game.dark_chess import Game
from engine.agents.agent import Agent
from engine.determinization.determinizer import Determinizer, RandomDeterminizer


class MonteCarloAgent(Agent):
    '''To choose a move, it plays <iterations> random games with each move, and chooses the won that wins the most'''
    def __init__(self, name: str, color: str, iterations: int = 300, determinizer=RandomDeterminizer()):
        self.name = name
        self.color = color
        self.iterations = iterations
        self.determinizer: Determinizer = determinizer


    def choose_move(self, game: Game):
        moves = game.get_legal_moves()
        
        if len(moves) == 1:
            return moves[0]

        scores = {x: 0.0 for x in range(len(moves))}
        
        sim_game = game.copy()

        for _ in range(self.iterations):
            det_game = self.determinizer.determinize_board(game, self.color)

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
    
    

class MCTSNode:
    def __init__(self, parent=None, move=None, color: str = "W"):
        self.parent = parent
        self.move = move
        self.color = color
        self.children = {}
        self.visits = 0
        self.value = 0.0

    def uct_value(self, exploration_constant: float = math.sqrt(2)) -> float:
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.value / self.visits
        parent_visits = self.parent.visits if self.parent else 1
        exploration = exploration_constant * math.sqrt(math.log(parent_visits) / self.visits)
        
        return exploitation + exploration


class MonteCarloTreeSearchAgent(Agent):
    """Uses a tree search to focus on moves that seem more promising"""
    def __init__(self, name: str, color: str, iterations: int = 100, exploration_constant: float = math.sqrt(2), determinizer=RandomDeterminizer()):
        self.name = name
        self.color = color
        self.iterations = iterations
        self.exploration_constant = exploration_constant
        self.determinizer: Determinizer = determinizer
        self.max_simulation_length = 200
        self.sim_game = Game()
    
    def choose_move(self, game: Game):
        moves = game.get_legal_moves()
        
        if len(moves) == 1:
            return moves[0]
        
        root = MCTSNode(parent=None, move=None, color=game.current_player)
        
        for _ in range(self.iterations):
            det_game = self.determinizer.determinize_board(game, self.color)
            
            leaf = self.select_and_expand(root, det_game)
            
            reward = self.simulate_game(det_game)
            
            self.backpropagate(leaf, reward)
        
        if not root.children:
            return random.choice(moves)
            
        best_move = max(root.children.values(), key=lambda child: child.visits).move
        return best_move
    
    def select_and_expand(self, node: MCTSNode, game: Game) -> MCTSNode:
        current = node
        
        while game.get_result() is None:
            legal_moves = game.get_legal_moves()
            
            if not legal_moves:
                break
                
            untried_moves = [m for m in legal_moves if m not in current.children]
            
            if untried_moves:
                move = random.choice(untried_moves)
                moving_player = game.current_player
                game.take_action(move)
                
                child = MCTSNode(parent=current, move=move, color=moving_player)
                current.children[move] = child
                return child
            else:
                legal_children = [current.children[m] for m in legal_moves if m in current.children]
                
                if not legal_children:
                    break
                    
                current = max(legal_children, key=lambda c: c.uct_value(self.exploration_constant))
                game.take_action(current.move)
    
        return current
    
    def simulate_game(self, game: Game) -> str:
        game.copy_into(self.sim_game)
        
        for _ in range(self.max_simulation_length):
            result = self.sim_game.get_result()
            
            if result is not None:
                return result
            
            moves = self.sim_game.get_legal_moves()
            
            if not moves:
                return "D"
            
            self.sim_game.take_action(random.choice(moves))
        
        return "D"
    
    def backpropagate(self, node: MCTSNode, reward: str) -> None:
        current = node

        while current is not None:
            current.visits += 1
            current.value += self.score_outcome(reward, current.color)
            current = current.parent
    
    def score_outcome(self, result: str, node_color: str) -> float:
        if result == node_color:
            return 1.0
        
        if result == "D":
            return 0.5
        
        return 0.0