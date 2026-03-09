from dataclasses import dataclass


@dataclass(frozen=True)
class Piece:
    kind: str
    color: str  # "W" or "B"

    @property
    def value(self) -> int:
        values = {
            "K": 1000,
            "Q": 9,
            "R": 5,
            "B": 3,
            "N": 3,
            "P": 1,
        }
        return values.get(self.kind, 0)

    def symbol(self) -> str:
        return self.kind if self.color == "W" else self.kind.lower()