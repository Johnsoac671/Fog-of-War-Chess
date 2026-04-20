import random
import math
import time
from datetime import timedelta
import json


from engine.game.dark_chess import Game
from engine.agents.agent import Agent
from engine.determinization.determinizer import Determinizer, RandomDeterminizer


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
    def __init__(self, name: str, color: str, iterations: int = 2000, exploration_constant: float = math.sqrt(2)):
        self.name = name
        self.color = color
        self.iterations = iterations
        self.exploration_constant = exploration_constant
        self.determinizer: Determinizer = RandomDeterminizer()
        self.max_simulation_length = 200
        self.sim_game = Game()
        self.memory = []
    
    def choose_move(self, game: Game):
        moves = game.get_legal_moves()
        
        if len(moves) == 1:
            policy = {str(moves[0]): 1.0}
            self.memory.append({
                "board_state": game.board.fen(),
                "policy": policy,
                "player_to_move": game.current_player
            })
            return moves[0]
        
        root = MCTSNode(parent=None, move=None, color=game.current_player)
        
        for _ in range(self.iterations):
            det_game = self.determinizer.determinize_board(game)
            leaf = self.select_and_expand(root, det_game)
            reward = self.simulate_game(det_game)
            self.backpropagate(leaf, reward)
        
        if not root.children:
            return random.choice(moves)
            
        total_visits = sum(child.visits for child in root.children.values())
        policy = {str(move): child.visits / total_visits for move, child in root.children.items()}
        
        self.memory.append({
            "board_state": game.board.fen(),
            "policy": policy,
            "player_to_move": game.current_player
        })
            
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


def generate_training_data(num_games: int):
    white_agent = MonteCarloTreeSearchAgent(name="MCTS_White", color="W", iterations=1000)
    black_agent = MonteCarloTreeSearchAgent(name="MCTS_Black", color="B", iterations=1000)
    
    results = {"W": 0, "B": 0, "D": 0}
    start_time = time.time()
    game = Game()
    for i in range(num_games):
        game.reset()
        winner = play_game(white_agent, black_agent, 100, game)
        results[winner] += 1
        
        elapsed = time.time() - start_time
        avg_time = elapsed / (i + 1)
        remaining = avg_time * (num_games - (i + 1))
        
        print(
            f"Game {i + 1}/{num_games} | "
            f"Winner: {winner} | "
            f"Elapsed: {str(timedelta(seconds=int(elapsed)))} | "
            f"ETA: {str(timedelta(seconds=int(remaining)))}"
        )
        
    print("\nGeneration Complete:")
    for key, value in results.items():
        print(f"{key}: {value}")


def play_game(white_agent, black_agent, max_turns, state) -> str:
    turns = 0

    white_agent.memory = []
    black_agent.memory = []

    while not state.get_result():
        if turns > max_turns:
            break
        
        agent = white_agent if state.current_player == "W" else black_agent
        move = agent.choose_move(state)

        if move is None:
            break

        state.take_action(move)
        turns += 1
        

    winner = state.get_result()
    if not winner: 
        winner = "D"
        
    
    full_game_memory = white_agent.memory + black_agent.memory
    
    with open("training_data.jsonl", "a") as f:
        for snapshot in full_game_memory:
            
            if winner == "D":
                z = 0.0 
            elif winner == snapshot["player_to_move"]:
                z = 1.0
            else:
                z = -1.0
                
            training_sample = {
                "state": snapshot["board_state"],
                "policy": snapshot["policy"],
                "value": z
            }
            
            f.write(json.dumps(training_sample) + "\n")

    return winner

if __name__ == "__main__":
    generate_training_data(1000)