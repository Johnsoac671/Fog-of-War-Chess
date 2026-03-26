from typing import List, Set, Tuple

from src.game.pieces import Piece

Position = Tuple[int, int]
Board = List[List[Piece | None]]


# check if a position is within the bounds of the board
def in_bounds(r: int, c: int, size: int = 5) -> bool:
    return 0 <= r < size and 0 <= c < size

# accepts current board state and the color of the player
# player is "W" or "B"
# returns a set of positions that the player can see
def get_visible_squares(board: Board, player: str) -> Set[Position]:
    """
    Simplified visibility:
    A player sees squares occupied by own pieces and squares those pieces can move to.
    This is a draft approximation of fog-of-war visibility.
    """
    visible: Set[Position] = set()
    size = len(board)

    for r in range(size):
        for c in range(size):
            # decide which squares this piece can see
            piece = board[r][c]
            if piece is None or piece.color != player:
                continue

            visible.add((r, c))

            directions = []
            if piece.kind == "P":
                # pawn
                step = -1 if player == "W" else 1
                for dc in (-1, 0, 1):
                    nr, nc = r + step, c + dc
                    if in_bounds(nr, nc, size):
                        visible.add((nr, nc))
                # handle pawn 2 move case
                if player == "W" and r == 3 and board[r-1][c] is None:
                    visible.add((r - 2, c))
                if player == "B" and r == 1 and board[r+1][c] is None:
                    visible.add((r + 2, c))
            elif piece.kind == "N":
                # knight
                jumps = [
                    (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                    (1, -2), (1, 2), (2, -1), (2, 1),
                ]
                for dr, dc in jumps:
                    nr, nc = r + dr, c + dc
                    if in_bounds(nr, nc, size):
                        visible.add((nr, nc))
            else:
                # rook, bishop, queen, king
                if piece.kind in ("R", "Q", "K"):
                    directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])
                if piece.kind in ("B", "Q", "K"):
                    directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

                max_steps = 1 if piece.kind == "K" else size
                for dr, dc in directions:
                    for step in range(1, max_steps + 1):
                        nr, nc = r + dr * step, c + dc * step
                        if not in_bounds(nr, nc, size):
                            break
                        visible.add((nr, nc))
                        if board[nr][nc] is not None:
                            # cant see through pieces
                            break

    return visible
