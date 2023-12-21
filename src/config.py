import json
from collections.abc import Callable
from pathlib import Path

Heuristic = Callable[[tuple[int, int], tuple[int, int]], float]


class Config:
    """
    Configuration manager.
    """
    def __init__(self) -> None:
        self._cfg: dict = {}

    @property
    def fps(self) -> int:
        """
        The Frames Per Second.
        """
        return self._cfg["fps"]

    @property
    def max_steps(self) -> int:
        """
        The maximum number of steps that the agent can move.
        """
        return self._cfg["maxSteps"]

    @property
    def map_size(self) -> dict[str, int]:
        """
        The size of game map.
        """
        return self._cfg["mapSize"]

    @property
    def terrain_prob(self) -> dict[str, float]:
        """
        The probability of generating each kind of terrain.
        """
        return self._cfg["terrainProb"]

    @property
    def move_cost(self) -> dict[str, float]:
        """
        The move cost of each kind of terrain.
        """
        return self._cfg["moveCost"]

    @property
    def heuristic(self) -> 'Heuristic':
        """
        The heuristic function.
        """
        def dist(src: tuple[int, int], dest: tuple[int, int]) -> float:
            return abs(src[0] - dest[0]) + abs(src[1] - dest[1])
        return dist

    def strategy_weights(self, role: str) -> dict[str, float]:
        """
        The weight for each strategy.
        """
        return self._cfg["strategyWeights"][role]

    def load(self, path: Path) -> None:
        """
        Load the configuration from a JSON file.
        """
        with path.open(encoding="utf-8") as file:
            self._cfg = json.load(file)
