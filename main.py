from engine.game.dark_chess import Game
from engine.agents.random_agents import RandomAgent
from engine.agents.monte_carlo_agent import MonteCarloAgent, MonteCarloTreeSearchAgent


def main() -> None:
    state = Game()

    white_agent = MonteCarloAgent(name="MonteCarlo", color="W")
    black_agent = MonteCarloTreeSearchAgent(name="MonteCarloTreeSearch", color="B")

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