from engine.game.dark_chess import Game
from engine.agents.random_agents import RandomAgent


def play_game(white_agent, black_agent, max_turns: int = 100) -> str:
    state = Game()
    turns = 0

    while not state.get_result():
        
        if turns > max_turns:
            return "D"
        
        agent = white_agent if state.current_player == "W" else black_agent
        move = agent.choose_move(state)

        if move is None:
            break

        state.take_action(move)
        turns += 1

    return state.get_result()


def run_matches(num_games: int = 10) -> None:
    white_agent = RandomAgent(name="RandomWhite")
    black_agent = RandomAgent(name="RandomBlack")

    results = {"W": 0, "B": 0, "D": 0}

    for i in range(num_games):
        winner = play_game(white_agent, black_agent)
        results[winner] += 1
        print(f"Game {i + 1}: Winner = {winner}")

    print("\nFinal Results:")
    for key, value in results.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    run_matches(100)