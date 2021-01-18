import json
from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from collections.abc import Callable

    Heuristic = Callable[[tuple[int, int], tuple[int, int]], float]


class Config:
    """
    Configuration manager.
    """
    def __init__(self) -> None:
        self._cfg: dict = {}

    @property
    def fps(self) -> int:
        return self._cfg["fps"]

    @property
    def max_steps(self) -> int:
        return self._cfg["maxSteps"]

    @property
    def map_size(self) -> dict[str, int]:
        return self._cfg["mapSize"]

    @property
    def terrain_prob(self) -> dict[str, float]:
        return self._cfg["terrainProb"]

    @property
    def move_cost(self) -> dict[str, float]:
        return self._cfg["moveCost"]

    @property
    def heuristic(self) -> Heuristic:
        def dist(src: tuple[int, int], dest: tuple[int, int]) -> float:
            return abs(src[0] - dest[0]) + abs(src[1] - dest[1])
        return dist

    def strategy_weights(self, role: str) -> dict[str, float]:
        return self._cfg["strategyWeights"][role]

    def load(self, path: Path) -> None:
        with path.open(encoding="utf-8") as file:
            self._cfg = json.load(file)
