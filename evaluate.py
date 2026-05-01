import time
import torch
from datetime import timedelta

from engine.game.dark_chess import Game
from engine.agents.random_agents import RandomAgent, SmartRandomAgent
from engine.agents.monte_carlo_agent import MonteCarloAgent, MonteCarloTreeSearchAgent
from engine.agents.neural_network_agents import NeuralMCTSAgent
from engine.agents.alpha_beta_agent import AlphaBetaAgent
from network_training import DarkChessNetwork
# import determinizers
from engine.determinization.determinizer import IgnoranceIsBlissDeterminizer, BadDeterminizer, RandomDeterminizer

def play_game(white_agent, black_agent, max_turns: int = 100) -> str:
    # state = Game(client_side=1)
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
        
        # print('-----')
        # print(f"{agent.name} chooses move: {move}")
        # ret = state.get_frontend_visualization()
        # for row in ret:
        #     print(''.join(row))
        # print('-----\n')
        
        turns += 1
        
    state.visualize(True)
    return state.get_result()

def run_matches(num_games: int = 10) -> None:
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # pre stuff for NeuralMCTSAgent agent (my GPU didnt work so used cpu)
    device = 'cpu'
    networkA = DarkChessNetwork().to(device)
    networkA.load_state_dict(torch.load("dark_chess.pth", map_location=device))
    networkA.eval()
    
    # round 1
    
    # 8 vs 9 seed
    # white_agent = MonteCarloTreeSearchAgent(name="", color="W", determinizer=RandomDeterminizer())
    # black_agent = AlphaBetaAgent(name="", color="B", determinizer=RandomDeterminizer())
    
    # 4 vs 13 seed
    # white_agent = NeuralMCTSAgent(name="", color="W", network=networkA, iterations=100, device='cpu', determinizer=RandomDeterminizer())
    # black_agent = MonteCarloAgent(name="", color="B", iterations=100, determinizer=IgnoranceIsBlissDeterminizer())
    
    # 5 vs 12 seed
    # white_agent = MonteCarloTreeSearchAgent(name="", color="W", iterations=100, determinizer=BadDeterminizer())
    # black_agent = RandomAgent(name="", color="B")
    
    # 7 vs 10 seed
    # white_agent = SmartRandomAgent(name="", color="W")
    # black_agent = NeuralMCTSAgent(name="", color="B", network=networkA, iterations=100, device='cpu', determinizer=IgnoranceIsBlissDeterminizer())
    
    # 3 vs 14 seed
    # white_agent = MonteCarloTreeSearchAgent(name="", color="W", iterations=200, determinizer=IgnoranceIsBlissDeterminizer())
    # black_agent = AlphaBetaAgent(name="", color="B", max_depth=2, determinizer=BadDeterminizer())
    
    # 6 vs 11 seed
    # white_agent = NeuralMCTSAgent(name="", color="W", network=networkA, iterations=50, device='cpu', determinizer=BadDeterminizer())
    # black_agent = MonteCarloAgent(name="", color="B", iterations=50, determinizer=BadDeterminizer())
    
    # round 2
    
    # 1 vs 8 seed
    # white_agent = MonteCarloAgent(name="", color="W", iterations=50, determinizer=RandomDeterminizer())
    # black_agent = MonteCarloTreeSearchAgent(name="", color="B", iterations=50, determinizer=RandomDeterminizer())
    
    # 4 vs 5 seed
    # white_agent = NeuralMCTSAgent(name="", color="W", network=networkA, iterations=100, device='cpu', determinizer=RandomDeterminizer())
    # black_agent = MonteCarloTreeSearchAgent(name="", color="B", iterations=100, determinizer=BadDeterminizer())
    
    # 2 vs 10 seed
    # white_agent = AlphaBetaAgent(name="", color="W", determinizer=IgnoranceIsBlissDeterminizer())
    # black_agent = NeuralMCTSAgent(name="", color="B", network=networkA, iterations=100, device='cpu', determinizer=IgnoranceIsBlissDeterminizer())

    # 14 vs 6 seed
    # white_agent = AlphaBetaAgent(name="", color="W", max_depth=2, determinizer=BadDeterminizer())
    # black_agent = NeuralMCTSAgent(name="", color="B", network=networkA, iterations=100, device='cpu', determinizer=BadDeterminizer())
    
    # semifinal
    
    # 1 vs 4 seed
    # white_agent = MonteCarloAgent(name="", color="W", iterations=50, determinizer=RandomDeterminizer())
    # black_agent = NeuralMCTSAgent(name="", color="B", network=networkA, iterations=50, device='cpu', determinizer=RandomDeterminizer())
    
    # 2 vs 14 seed
    # white_agent = AlphaBetaAgent(name="", color="W", determinizer=IgnoranceIsBlissDeterminizer())
    # black_agent = AlphaBetaAgent(name="", color="B", max_depth=2, determinizer=BadDeterminizer())
    
    # final
    white_agent = AlphaBetaAgent(name="", color="W", determinizer=IgnoranceIsBlissDeterminizer())
    black_agent = NeuralMCTSAgent(name="", color="B", network=networkA, iterations=200, device='cpu', determinizer=RandomDeterminizer())
    
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
    run_matches(25)