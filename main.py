from src.game.state import GameState
from src.agents.random_agent import RandomAgent
from src.agents.minimax_agent import MinimaxAgent


def main() -> None:
    state = GameState.initial_state()

    white_agent = MinimaxAgent(name="MinimaxWhite", depth=2)
    black_agent = RandomAgent(name="RandomBlack")

    print("Starting game...\n")
    print(state)

    while not state.is_terminal():
        agent = white_agent if state.current_player == "W" else black_agent
        move = agent.choose_move(state)

        if move is None:
            print(f"{agent.name} has no legal moves.")
            break

        print(f"\n{agent.name} chooses move: {move}")
        state = state.apply_move(move)
        print(state)

    winner = state.get_winner()
    print("\nGame Over")
    print(f"Winner: {winner}")


if __name__ == "__main__":
    main()