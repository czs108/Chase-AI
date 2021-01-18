from typing import TYPE_CHECKING
from enum import Enum, auto
from random import random
import math

from grid import Grid
from game import cfg

if TYPE_CHECKING:
    from game.role import Enemy, Agent


class Terrain(Enum):
    WALL = auto()
    GRASS = auto()
    BUSH = auto()

    def move_cost(self) -> float:
        name = self.name.lower()
        return cfg.move_cost[name] if name in cfg.move_cost else math.inf


class Map(Grid):
    def __init__(self, width: int, height: int) -> None:
        assert width > 1 and height > 1

        wall = Terrain.WALL.name.lower()
        bush = Terrain.BUSH.name.lower()
        prob = cfg.terrain_prob
        if not 0 <= prob[wall] < 1 or not 0 <= prob[bush] <= 1:
            raise ValueError("Invalid probability of terrain.")

        def random_terrain():
            if random() < prob[wall]:
                return Terrain.WALL
            elif random() < prob[bush]:
                return Terrain.BUSH
            else:
                return Terrain.GRASS

        spots = [[None] * height for _ in range(width)]
        for x in range(width):
            for y in range(height):
                spots[x][y] = random_terrain()
        super().__init__(spots)

    def terrain(self, x: int, y: int) -> Terrain:
        return self.spot(x, y) if self.valid(x, y) else Terrain.WALL

    def wall(self, x: int, y: int) -> bool:
        return self.terrain(x, y) == Terrain.WALL

    def blanks(self) -> list[tuple[int, int]]:
        spots = []
        for x in range(self.width):
            for y in range(self.height):
                if not self.wall(x, y):
                    spots.append((x, y))
        return spots

    def occupied(self, x: int, y: int, status: Status) -> Occupy:
        if not self.valid(x, y):
            return Occupy.INVALID
        elif self.wall(x, y):
            return Occupy.WALL
        elif (status.agent and (x, y) == status.agent.pos) or (status.enemy and (x, y) == status.enemy.pos):
            return Occupy.ROLE
        else:
            return Occupy.NONE

    def move_cost(self, x: int, y: int) -> float:
        return self.terrain(x, y).move_cost()


class Occupy(Enum):
    """
    The result of occupation check.
    """
    # No occupation.
    NONE = auto()

    # The position is invalid.
    INVALID = auto()

    # The position is a wall.
    WALL = auto()

    # The position is occupied by a role.
    ROLE = auto()


class Status:
    _CLOSE_DIST: int = 2
    """
    The status of a level.
    """

    def __init__(self) -> None:
        self.agent: Agent = None
        self.enemy: Enemy = None
        self._steps: int = 1
        self._good_steps: int = 0
        self._game_end: bool = False

    @property
    def game_end(self) -> bool:
        return self._game_end

    @property
    def score(self) -> int:
        return int(self._good_steps / self._steps * 100)

    @property
    def steps(self) -> int:
        return self._steps

    @property
    def good_steps(self) -> int:
        return self._good_steps

    def new_step(self) -> None:
        assert not self._game_end
        self._steps += 1

        def good_step() -> bool:
            agent_pos = self.agent.pos
            enemy_pos = self.enemy.pos
            return abs(enemy_pos[0] - agent_pos[0]) >= self._CLOSE_DIST \
                   and abs(enemy_pos[1] - agent_pos[1]) >= self._CLOSE_DIST

        if good_step():
            self._good_steps += 1

    def end_game(self) -> None:
        self._game_end = True

    def opponent(self, role: Agent | Enemy) -> Agent | Enemy:
        if role is self.agent:
            return self.enemy
        elif role is self.enemy:
            return self.agent
        else:
            assert False
