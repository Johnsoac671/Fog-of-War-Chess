import os
import glob
import re
import torch
from engine.game.dark_chess import Game
from engine.agents.neural_network_agents import NeuralMCTSAgent

from training_data_generator import start_batched_generation
from network_training import DarkChessNetwork, train_network, get_recent_dataset_files

def get_latest_version():
    files = glob.glob(os.path.join(".", f"{"dark_chess_v"}*{".pth"}"))
    
    def extract_version(f):
        match = re.search(r'_v(\d+)\.pth', f)
        return int(match.group(1)) if match else 0
    
    if not files:
        return 0
    
    return max([extract_version(f) for f in files])

def play_arena(old_model_path, new_model_path, num_games=40, mcts_iters=150):
    
    print(f"\n--- Beginning Comparison ---")
    print(f"{new_model_path} Vs {old_model_path}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    old_net = DarkChessNetwork().to(device)
    if os.path.exists(old_model_path):
        old_net.load_state_dict(torch.load(old_model_path, map_location=device))
    old_net.eval()

    new_net = DarkChessNetwork().to(device)
    new_net.load_state_dict(torch.load(new_model_path, map_location=device))
    new_net.eval()

    new_wins = 0
    old_wins = 0
    draws = 0

    for i in range(num_games):
        state = Game()
        
        if i % 2 == 0:
            white_agent = NeuralMCTSAgent("New_Model", "W", network=new_net, iterations=mcts_iters)
            black_agent = NeuralMCTSAgent("Old_Model", "B", network=old_net, iterations=mcts_iters)
        else:
            white_agent = NeuralMCTSAgent("Old_Model", "W", network=old_net, iterations=mcts_iters)
            black_agent = NeuralMCTSAgent("New_Model", "B", network=new_net, iterations=mcts_iters)

        while not state.get_result():
            agent = white_agent if state.current_player == "W" else black_agent
            move = agent.choose_move(state) 
            
            if move is None: 
                break
            
            state.take_action(move)

        winner = state.get_result()
        if winner == "D":
            draws += 1
        else:
            winner_agent = white_agent if winner == "W" else black_agent
            if winner_agent.name == "New_Model":
                new_wins += 1
            else:
                old_wins += 1
                
        print(f"Game {i+1}/{num_games} complete. Score -> New: {new_wins} | Old: {old_wins} | Draws: {draws}")

    win_rate = (new_wins + (0.5 * draws)) / num_games
    print(f"Arena Complete! New Model Win Rate: {win_rate * 100:.1f}%")
    return win_rate

def run_autonomous_loop(total_generations=10, games_per_gen=1500, workers=12):
    for _ in range(total_generations):
        latest_version = get_latest_version()
        target_version = latest_version + 1
        
        current_model_path = f"dark_chess_v{latest_version}.pth" if latest_version > 0 else ""
        new_data_path = f"training_data_v{target_version}.jsonl"
        new_model_path = f"dark_chess_v{target_version}.pth"
        
        print(f" STARTING VERSION {target_version}")
        
        print(f"\nGenerating {games_per_gen} training games...")
        
        start_batched_generation(
            total_games=games_per_gen, 
            num_workers=workers, 
            load_model_path=current_model_path, 
            output_data_path=new_data_path
        )
        
        print(f"\nTraining darh_chess_v{target_version}...")
        sliding_window_files = get_recent_dataset_files(5)
        print(f"Using datasets: {sliding_window_files}")
        
        net = DarkChessNetwork()
        if current_model_path and os.path.exists(current_model_path):
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            net.load_state_dict(torch.load(current_model_path, map_location=device))
            
        train_network(model=net, dataset_paths=sliding_window_files, save_path=new_model_path, epochs=3)
        
        if latest_version > 0:
            print(f"\nEvaluating Models...")

            win_rate = play_arena(current_model_path, new_model_path, num_games=40)
            

            if win_rate > 0.55:
                print(f"New Version Better :)")
            else:
                print(f"New Version Worse :(")
                os.remove(new_model_path)

if __name__ == "__main__":
    run_autonomous_loop(total_generations=50, games_per_gen=2000, workers=11)