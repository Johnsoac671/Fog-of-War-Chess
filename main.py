import time
import torch
from datetime import timedelta

from engine.game.dark_chess import Game
from engine.agents.random_agents import RandomAgent, SmartRandomAgent
from engine.agents.monte_carlo_agent import MonteCarloAgent, MonteCarloTreeSearchAgent
from engine.agents.neural_network_agents import NeuralMCTSAgent
from engine.agents.alpha_beta_agent import AlphaBetaAgent
from network_training import DarkChessNetwork


def main() -> None:
    state = Game()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    network = DarkChessNetwork().to(device)
    network.load_state_dict(torch.load("dark_chess.pth", map_location=device))
    network.eval()
    
    white_agent = NeuralMCTSAgent(name="Neural", color="W", network=network, iterations=1000)
    black_agent = RandomAgent(name="rando", color="B")

    print("Starting game...\n")
    state.visualize()

    while not state.get_result():
        agent = white_agent if state.current_player == "W" else black_agent
        move = agent.choose_move(state)

        if move is None: # i don't *think* this can ever actually happen, since this is just what checkmate is, but probably a good idea to keep it
            print(f"{agent.name} has no legal moves.")
            break

        print(f"\n{agent.name} chooses move: {move}")
        state.take_action(move)
        state.visualize(True)

    winner = state.get_result()
    print("\nGame Over")
    print(f"Winner: {white_agent.name if winner == "W" else black_agent.name if winner == "B" else "Draw"}")


if __name__ == "__main__":
    main()