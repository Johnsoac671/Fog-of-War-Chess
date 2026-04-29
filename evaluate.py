import time
import torch
from datetime import timedelta

from engine.game.dark_chess import Game
from engine.agents.random_agents import RandomAgent, EagerRandomAgent
from engine.agents.monte_carlo_agent import MonteCarloAgent, MonteCarloTreeSearchAgent
from engine.agents.neural_network_agents import NeuralMCTSAgent
from engine.agents.alpha_beta_agent import AlphaBetaAgent
from network_training import DarkChessNetwork

def play_game(white_agent, black_agent, max_turns: int = 100) -> str:
    state = Game()
        
    turns = 0

    while not state.get_result():
        if turns > max_turns:
            return "D"
        
        agent = white_agent if state.current_player == "W" else black_agent
        move = agent.choose_move(state)

        if move is None:
            return "D"

        state.take_action(move)
        turns += 1
        
    state.visualize(True)
    return state.get_result()

def run_matches(num_games: int = 10) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    networkA = DarkChessNetwork().to(device)
    networkA.load_state_dict(torch.load("dark_chess.pth", map_location=device))
    networkA.eval()
    
    
    white_agent = NeuralMCTSAgent(name="Neural", color="W", network=networkA, iterations=300)
    black_agent = MonteCarloTreeSearchAgent(name="MCTS", color="B", iterations=300)

    results = {"W": 0, "B": 0, "D": 0}
    start = time.time()
    
    for i in range(num_games):
        winner = play_game(white_agent, black_agent)
        results[winner] += 1
        
        elapsed = time.time() - start
        avg = elapsed / (i + 1)
        remaining = avg * (num_games - (i + 1))
        
        print(
            f"Game {i + 1}: Winner = {winner} | "
            f"Elapsed: {str(timedelta(seconds=int(elapsed)))} | "
            f"ETA: {str(timedelta(seconds=int(remaining)))} | "
            f"{i + 1}/{num_games}"
        )

    print("\nFinal Results:")
    for key, value in results.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    run_matches(100)