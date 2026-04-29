import random
import math
import time
from datetime import timedelta
import json
import numpy as np
import torch
import torch.nn as nn
import multiprocessing as mp

from engine.game.dark_chess import Game
from engine.agents.neural_network_agents import RemoteNeuralMCTSAgent

from network_training import DarkChessNetwork



def self_play_worker(worker_id: int, num_games: int, req_queue: mp.Queue, resp_pipe, output_file: str):
    white_agent = RemoteNeuralMCTSAgent("W_Agent", "W", worker_id, req_queue, resp_pipe, iterations=300)
    black_agent = RemoteNeuralMCTSAgent("B_Agent", "B", worker_id, req_queue, resp_pipe, iterations=300)
    game = Game()
    
    for _ in range(num_games):
        game.reset()
        turns = 0
        white_agent.memory, black_agent.memory = [], []
        
        while not game.get_result() and turns <= 100:
            agent = white_agent if game.current_player == "W" else black_agent
            temperature = 1.0 if turns < 25 else 0.0
            move = agent.choose_move(game, temperature=temperature)
            if move is None: break
            game.take_action(move)
            turns += 1
            
        winner = game.get_result() or "D"
        full_memory = white_agent.memory + black_agent.memory
        
        with open(output_file, "a") as f:
            for snapshot in full_memory:
                z = 1.0 if winner == snapshot["player_to_move"] else (0.0 if winner == "D" else -1.0)
                f.write(json.dumps({"state": snapshot["board_state"], "policy": snapshot["policy"], "value": z}) + "\n")
                
    req_queue.put((worker_id, "DONE"))


def start_batched_generation(total_games: int, num_workers: int, load_model_path: str, output_data_path: str):
    import os
    mp.set_start_method('spawn', force=True)
    
    estimated_moves_per_game = 45
    target_states = total_games * estimated_moves_per_game
    current_states = 0
    
    if os.path.exists(output_data_path):
        with open(output_data_path, 'r') as f:
            current_states = sum(1 for _ in f)
            
    if current_states >= target_states:
        print(f"Data file {output_data_path} already has {current_states} states. Target met! Skipping generation.")
        return
        
    remaining_states = target_states - current_states
    remaining_games = max(num_workers, remaining_states // estimated_moves_per_game)
    
    print(f"File has {current_states} states. Target is ~{target_states}.")
    print(f"Generating approx {remaining_games} more games to meet target...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Inference Server booting up on {device}...")
    
    model = DarkChessNetwork()
    
    if load_model_path and os.path.exists(load_model_path):
        print(f"Generator loading model: {load_model_path}")
        model.load_state_dict(torch.load(load_model_path, map_location=device))
    else:
        print("No prior model found. Generator using random weights.")
    
    model.to(device)
    model.eval()

    req_queue = mp.Queue()
    worker_pipes = {}
    processes = []
    
    games_per_worker = remaining_games // num_workers
    
    for i in range(num_workers):
        parent_conn, child_conn = mp.Pipe()
        worker_pipes[i] = parent_conn
        
        p = mp.Process(target=self_play_worker, args=(i, games_per_worker, req_queue, child_conn, output_data_path))
        p.start()
        processes.append(p)
        
    print(f"Spawned {num_workers} workers. Starting Batched Inference loop.")
    
    active_workers = num_workers
    max_batch_size = 64
    
    while active_workers > 0:
        batch_ids = []
        batch_tensors = []
        
        worker_id, data = req_queue.get()
        
        if isinstance(data, str) and data == "DONE":
            active_workers -= 1
            continue
            
        batch_ids.append(worker_id)
        batch_tensors.append(data)
        
        while len(batch_ids) < max_batch_size and not req_queue.empty():
            worker_id, data = req_queue.get()
            if isinstance(data, str) and data == "DONE":
                active_workers -= 1
            else:
                batch_ids.append(worker_id)
                batch_tensors.append(data)
                
        tensor_batch = torch.tensor(np.concatenate(batch_tensors, axis=0)).to(device)
        
        with torch.inference_mode():
            policy_batch, value_batch = model(tensor_batch)
            
        policy_batch = policy_batch.cpu().numpy()
        value_batch = value_batch.cpu().numpy()
        
        for idx, w_id in enumerate(batch_ids):
            worker_pipes[w_id].send((policy_batch[idx], value_batch[idx][0]))

    for p in processes:
        p.join()
        
    print("All workers finished. Generation Complete!")


if __name__ == "__main__":
    start_batched_generation(total_games=1, num_workers=12)