import random
import math
import torch
import numpy as np
import multiprocessing as mp

from engine.game.dark_chess import Game
from engine.agents.agent import Agent
from engine.determinization.determinizer import Determinizer, RandomDeterminizer
from engine.util.util import board_to_numpy


class MCTSNode:
    def __init__(self, parent=None, move=None, color: str = "W", prior: float = 0.0):
        self.parent = parent
        self.move = move
        self.color = color
        self.children = {}
        self.visits = 0
        self.value = 0.0
        self.prior = prior
    
    def puct_value(self, c_puct: float = 1.5) -> float:
        q_value = (1.0 - (self.value / self.visits)) if self.visits > 0 else 0.5
        
        parent_visits = self.parent.visits if self.parent else 1
        u_value = c_puct * self.prior * math.sqrt(parent_visits) / (1 + self.visits)
        return q_value + u_value


class NeuralMCTSAgent(Agent):
    """Monte Carlo Tree Search, but it uses a Neural Network to rate how good various starting moves are, to determine which branches to explore more"""
    def __init__(self, name: str, color: str, network, iterations: int = 300,
                 exploration_constant: float = 1.5, determinizer=RandomDeterminizer(),
                 device=torch.device("cuda" if torch.cuda.is_available() else "cpu")):
        self.name = name
        self.color = color
        self.iterations = iterations
        self.exploration_constant = exploration_constant
        self.determinizer: Determinizer = determinizer
        self.value_network = network 
        self.device = device
        self.memory = []

    def get_move_index(self, move):
        (i, j), (dx, dy), _ = move
        return (i * 5 + j) * 25 + ((i + dx) * 5 + (j + dy))
      

    def choose_move(self, game: Game, temperature: float = 0.0):
        moves = game.get_legal_moves()
        
        if len(moves) == 1: 
            return moves[0]
            
        root = MCTSNode(parent=None, move=None, color=game.current_player)
        self.value_network.eval()
        
        board_numpy = board_to_numpy(game)
        board_tensor = torch.tensor(board_numpy, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        with torch.inference_mode():
            policy_odds, _ = self.value_network(board_tensor)
        
        policy_odds = policy_odds[0].cpu().numpy()
        legal_indices = [self.get_move_index(m) for m in moves]
        
        max_precentage_found = float('-inf')
        for idx in legal_indices:
            if policy_odds[idx] > max_precentage_found: max_precentage_found = policy_odds[idx]
                
        sum_exp = 0.0
        move_probs = {}
        for move, idx in zip(moves, legal_indices):
            exp_val = math.exp(policy_odds[idx] - max_precentage_found)
            move_probs[move] = exp_val
            sum_exp += exp_val
            
        for move in moves:
            prob = move_probs[move] / sum_exp if sum_exp > 0 else 1.0 / len(moves)
            root.children[move] = MCTSNode(parent=root, move=move, color=game.current_player, prior=prob)

        for _ in range(self.iterations):
            det_game = self.determinizer.determinize_board(game, self.color)
            leaf, value = self.select_and_evaluate(root, det_game)
            self.backpropagate(leaf, value)
            
        if not root.children: 
            return random.choice(moves)
            
        if temperature > 0.0:
            visits = [child.visits for child in root.children.values()]
            moves_list = list(root.children.values())
            total_visits = sum(visits)
            probs = [v / total_visits for v in visits]
            chosen_child = np.random.choice(moves_list, p=probs)
            return chosen_child.move
        
        else:
            return max(root.children.values(), key=lambda child: child.visits).move
    
    
    def select_and_evaluate(self, node: MCTSNode, game: Game):
        current = node
        while current.children and game.get_result() is None:
            current = max(current.children.values(), key=lambda c: c.puct_value(self.exploration_constant))
            game.take_action(current.move)
            
        result = game.get_result()
        if result is not None:
            prev_player = "W" if game.current_player == "B" else "B"
            reward = 1.0 if result == prev_player else (0.5 if result == "D" else 0.0)
            return current, 1.0 - reward 
            
        board_numpy = board_to_numpy(game)
        board_tensor = torch.tensor(board_numpy, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        with torch.inference_mode():
            policy_odds, nn_value = self.value_network(board_tensor)
            
        value = nn_value.item()
        policy_odds = policy_odds[0].cpu().numpy()
        legal_moves = game.get_legal_moves()
        
        move_probs = {}
        max_precentage_found = float('-inf')
        legal_indices = [self.get_move_index(m) for m in legal_moves]
        for idx in legal_indices:
            if policy_odds[idx] > max_precentage_found: max_precentage_found = policy_odds[idx]
                
        sum_exp = 0.0
        for move, idx in zip(legal_moves, legal_indices):
            exp_val = math.exp(policy_odds[idx] - max_precentage_found)
            move_probs[move] = exp_val
            sum_exp += exp_val
            
        for move in legal_moves:
            prob = move_probs[move] / sum_exp if sum_exp > 0 else 1.0 / len(legal_moves)
            current.children[move] = MCTSNode(parent=current, move=move, color=game.current_player, prior=prob)
            
        return current, value
    
    
    def backpropagate(self, node: MCTSNode, value: float) -> None:
        current, current_value = node, value
        
        while current is not None:
            current.visits += 1
            current.value += current_value
            current = current.parent
            current_value = 1.0 - current_value


# AI generated class; setup to make generating training data faster
class RemoteNeuralMCTSAgent(Agent):
    def __init__(self, name: str, color: str, worker_id: int, req_queue: mp.Queue, resp_pipe, iterations: int = 300, exploration_constant: float = 1.5, determinizer=RandomDeterminizer):
        self.name = name
        self.color = color
        self.worker_id = worker_id
        self.req_queue = req_queue
        self.resp_pipe = resp_pipe
        self.iterations = iterations
        self.exploration_constant = exploration_constant
        self.determinizer: Determinizer = determinizer()
        self.memory = []

    def get_move_index(self, move):
        (i, j), (dx, dy), promotion = move
        return (i * 5 + j) * 25 + ((i + dx) * 5 + (j + dy))

    def choose_move(self, game: Game, temperature):
        moves = game.get_legal_moves()
        if len(moves) == 1: return moves[0]
            
        root = MCTSNode(parent=None, move=None, color=game.current_player)
        
        board_array = np.expand_dims(board_to_numpy(game), axis=0)
        self.req_queue.put((self.worker_id, board_array))
        policy_logits, _ = self.resp_pipe.recv()
        
        legal_indices = [self.get_move_index(m) for m in moves]
        max_logit = float('-inf')
        for idx in legal_indices:
            if policy_logits[idx] > max_logit: max_logit = policy_logits[idx]
                
        sum_exp = 0.0
        move_probs = {}
        for move, idx in zip(moves, legal_indices):
            exp_val = math.exp(policy_logits[idx] - max_logit)
            move_probs[move] = exp_val
            sum_exp += exp_val
            
        for move in moves:
            prob = move_probs[move] / sum_exp if sum_exp > 0 else 1.0 / len(moves)
            root.children[move] = MCTSNode(parent=root, move=move, color=game.current_player, prior=prob)

        for _ in range(self.iterations):
            det_game = self.determinizer.determinize_board(game, self.color)
            leaf, value = self.select_and_evaluate(root, det_game)
            self.backpropagate(leaf, value)
            
        if not root.children: return random.choice(moves)
            
        total_visits = sum(child.visits for child in root.children.values())
        policy_vector = np.zeros(625, dtype=np.float32)
        for move, child in root.children.items():
            policy_vector[self.get_move_index(move)] = child.visits / total_visits
            
        self.memory.append({
            "board_state": board_to_numpy(game).tolist(),
            "policy": policy_vector.tolist(),
            "player_to_move": game.current_player
        })
        
        if temperature > 0.0:
            visits = [child.visits for child in root.children.values()]
            moves_list = list(root.children.values())
            probs = [v / total_visits for v in visits]
            chosen_child = np.random.choice(moves_list, p=probs)
            return chosen_child.move
        else:
            return max(root.children.values(), key=lambda child: child.visits).move
    
    def select_and_evaluate(self, node: MCTSNode, game: Game):
        current = node
        while current.children and game.get_result() is None:
            current = max(current.children.values(), key=lambda c: c.puct_value(self.exploration_constant))
            game.take_action(current.move)
            
        result = game.get_result()
        if result is not None:
            prev_player = "W" if game.current_player == "B" else "B"
            reward = 1.0 if result == prev_player else (0.5 if result == "D" else 0.0)
            return current, 1.0 - reward 
            
        board_array = np.expand_dims(board_to_numpy(game), axis=0)
        self.req_queue.put((self.worker_id, board_array))
        policy_logits, value = self.resp_pipe.recv()
        
        legal_moves = game.get_legal_moves()
        move_probs = {}
        max_logit = float('-inf')
        legal_indices = [self.get_move_index(m) for m in legal_moves]
        
        for idx in legal_indices:
            if policy_logits[idx] > max_logit: max_logit = policy_logits[idx]
                
        sum_exp = 0.0
        for move, idx in zip(legal_moves, legal_indices):
            exp_val = math.exp(policy_logits[idx] - max_logit)
            move_probs[move] = exp_val
            sum_exp += exp_val
            
        for move in legal_moves:
            prob = move_probs[move] / sum_exp if sum_exp > 0 else 1.0 / len(legal_moves)
            current.children[move] = MCTSNode(parent=current, move=move, color=game.current_player, prior=prob)
            
        return current, value
    
    def backpropagate(self, node: MCTSNode, value: float) -> None:
        current, current_value = node, value
        while current is not None:
            current.visits += 1
            current.value += current_value
            current = current.parent
            current_value = 1.0 - current_value