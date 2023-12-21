from collections.abc import Sequence
from typing import TypeVar, Optional

T = TypeVar("T")


class Grid:
    """
    The grid manager.
    """
    def __init__(self, spots: Sequence[Sequence[T]]) -> None:
        """
        The constructor.

        -- PARAMETERS --
        spots: A 2D array of spots. They will be the elements of grid.
        """
        self._spots: Sequence[Sequence[T]] = spots

    @property
    def spots(self) -> Sequence[Sequence[T]]:
        return self._spots

    @property
    def width(self) -> int:
        return len(self._spots)

    @property
    def height(self) -> int:
        return len(self._spots[0])

    def delete(self, x: int, y: int) -> None:
        """
        Delete a spot.
        """
        self._spots[x][y] = None

    def valid(self, x: int, y: int) -> bool:
        """
        Check if there is a spot at a position.
        """
        if x < 0 or x >= self.width:
            return False
        elif y < 0 or y >= self.height:
            return False
        elif self._spots[x][y] is None:
            return False
        else:
            return True

    def spot(self, x: int, y: int) -> Optional[T]:
        """
        Get the spot at a position.
        """
        return self._spots[x][y] if self.valid(x, y) else None

    def neighbors(self, x: int, y: int) -> list[T]:
        """
        Get neighbor spots of a position.
        """
        if not self.valid(x, y):
            return []
        spots = []
        if self.valid(x + 1, y):
            spots.append(self._spots[x + 1][y])
        if self.valid(x - 1, y):
            spots.append(self._spots[x - 1][y])
        if self.valid(x, y + 1):
            spots.append(self._spots[x][y + 1])
        if self.valid(x, y - 1):
            spots.append(self._spots[x][y - 1])
        return spots
