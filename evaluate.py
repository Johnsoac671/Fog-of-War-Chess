from src.game.state import GameState
from src.agents.random_agent import RandomAgent
from src.agents.minimax_agent import MinimaxAgent


def play_game(white_agent, black_agent, max_turns: int = 100) -> str:
    state = GameState.initial_state()
    turns = 0

    while not state.is_terminal() and turns < max_turns:
        agent = white_agent if state.current_player == "W" else black_agent
        move = agent.choose_move(state)

        if move is None:
            break

        state = state.apply_move(move)
        turns += 1

    return state.get_winner()


def run_matches(num_games: int = 10) -> None:
    white_agent = MinimaxAgent(name="MinimaxWhite", depth=2)
    black_agent = RandomAgent(name="RandomBlack")

    results = {"W": 0, "B": 0, "Draw": 0}

    for i in range(num_games):
        winner = play_game(white_agent, black_agent)
        results[winner] += 1
        print(f"Game {i + 1}: Winner = {winner}")

    print("\nFinal Results:")
    for key, value in results.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    run_matches(10)