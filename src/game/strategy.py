from random import randint
from collections.abc import Sequence

from game import cfg
from game.action import Action
from grid import Grid
import game.map as gm
import game.role as gr

ActionLevels = dict[Action, float]


class _Spot:
    """
    Used by A* path-finding.
    """
    def __init__(self, x: int, y: int) -> None:
        self._pos: tuple[int, int] = (x, y)
        self.prev: '_Spot' = None

        self.g: float = 0
        self.h: float = 0

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @property
    def x(self) -> int:
        return self._pos[0]

    @property
    def y(self) -> int:
        return self._pos[1]

    @property
    def f(self) -> float:
        return self.g + self.h

    def clear(self) -> None:
        self.prev = None
        self.g = 0
        self.h = 0

    def retrace(self) -> list['_Spot']:
        """
        Retrace the path to the current spot.
        """
        path = [self]
        spot = self
        while spot.prev:
            path.insert(0, spot.prev)
            spot = spot.prev
        return path


class Strategy:
    """
    The interface of action strategy.
    """
    MAX_ACTION_LVL: float = 10

    @staticmethod
    def new_init_lvls() -> ActionLevels:
        """
        Create an initial recommendation array.
        """
        return {action: 0 for action in Action}

    def __init__(self, role: 'gr.Role') -> None:
        self._role: 'gr.Role' = role

    def action_lvls(self, status: 'gm.Status') -> ActionLevels:
        """
        Get an array containing the level of recommendation for every action.
        Subclasses should implement their logic.
        """
        assert False

    def _delete_invalid(self, lvls: ActionLevels) -> ActionLevels:
        """
        Delete invalid actions.
        """
        for action in Action:
            dest = action.dest(self._role.pos)
            invalid = not self._role.map.valid(*dest)
            wall = not invalid and self._role.revealed(dest) and self._role.map.wall(*dest)
            if invalid or wall:
                lvls[action] = 0
        return lvls


class ActionSelector:
    """
    Choose the action according to the specific weights.
    """
    @staticmethod
    def equality(strategy_num: int) -> 'ActionSelector':
        """
        Create a default selector with all weights equal to 1.
        """
        return ActionSelector([1] * strategy_num)

    def __init__(self, weights: Sequence[float]) -> None:
        self.weights: Sequence[float] = weights

    def highest(self, lvl_matrix: Sequence[ActionLevels]) -> Action:
        """
        Choose the action with the highest level of recommendation.
        """
        if len(lvl_matrix) == 0:
            return Action.STAY

        total = Strategy.new_init_lvls()

        def merge(lvls: ActionLevels, weight: float) -> None:
            """
            Merge two recommendation arrays.
            """
            assert len(lvls) == len(total)
            for action in Action:
                total[action] += lvls[action] * weight

        for i in range(len(self.weights)):
            merge(lvl_matrix[i], self.weights[i])

        # If two or more actions have the same level, get a random one.
        choices = []
        best = Action(0)
        for action in Action:
            if total[action] > total[best]:
                choices = [action]
                best = action
            elif total[action] == total[best]:
                choices.append(action)
        return choices[randint(0, len(choices) - 1)]


class Random(Strategy):
    """
    Choose an action randomly.
    """
    @staticmethod
    def name() -> str:
        return "random"

    def action_lvls(self, status: 'gm.Status') -> ActionLevels:
        lvls = self.new_init_lvls()
        for action in Action:
            lvls[action] = randint(0, int(self.MAX_ACTION_LVL))
        self._delete_invalid(lvls)
        lvls[Action.STAY] = 0

        max_action = Action(0)
        for action in Action:
            if lvls[action] > lvls[max_action]:
                max_action = action
        lvls[max_action] = self.MAX_ACTION_LVL
        return lvls


class MoveAway(Strategy):
    """
    Choose an action to move away to the target.
    """
    @staticmethod
    def name() -> str:
        return "moveAway"

    def action_lvls(self, status: 'gm.Status') -> ActionLevels:
        target = status.opponent(self._role)
        lvls = self.new_init_lvls()
        if self._role.pos[0] >= target.pos[0]:
            lvls[Action.RIGHT] = Strategy.MAX_ACTION_LVL
        else:
            lvls[Action.LEFT] = Strategy.MAX_ACTION_LVL

        if self._role.pos[1] >= target.pos[1]:
            lvls[Action.UP] = Strategy.MAX_ACTION_LVL
        else:
            lvls[Action.DOWN] = Strategy.MAX_ACTION_LVL
        return self._delete_invalid(lvls)


class MoveClose(Strategy):
    """
    Choose an action to move closer to the target.
    """
    @staticmethod
    def name() -> str:
        return "moveClose"

    def action_lvls(self, status: 'gm.Status') -> ActionLevels:
        target = status.opponent(self._role)
        lvls = self.new_init_lvls()
        if self._role.pos[0] > target.pos[0]:
            lvls[Action.LEFT] = Strategy.MAX_ACTION_LVL
        elif self._role.pos[0] < target.pos[0]:
            lvls[Action.RIGHT] = Strategy.MAX_ACTION_LVL

        if self._role.pos[1] > target.pos[1]:
            lvls[Action.DOWN] = Strategy.MAX_ACTION_LVL
        elif self._role.pos[1] < target.pos[1]:
            lvls[Action.UP] = Strategy.MAX_ACTION_LVL
        return self._delete_invalid(lvls)


class WallDensity(Strategy):
    """
    Find a direction where the density of walls is lower.
    """
    _RANGE: int = 5

    @staticmethod
    def name() -> str:
        return "wallDensity"

    def action_lvls(self, status: 'gm.Status') -> ActionLevels:
        lvls = self.new_init_lvls()
        for action in Action:
            lvls[action] = (1 - self._density(action)) * Strategy.MAX_ACTION_LVL
        lvls[Action.STAY] = 0
        return self._delete_invalid(lvls)

    def _density(self, action: Action) -> float:
        """
        Calculate the density of wall in a direction.
        """
        pos = self._role.pos
        if action == Action.LEFT:
            begin = (pos[0] - self._RANGE, pos[1] - self._RANGE)
            end = (pos[0], pos[1] + self._RANGE)
        elif action == Action.RIGHT:
            begin = (pos[0], pos[1] - self._RANGE)
            end = (pos[0] + self._RANGE, pos[1] + self._RANGE)
        elif action == Action.UP:
            begin = (pos[0] - self._RANGE, pos[1])
            end = (pos[0] + self._RANGE, pos[1] + self._RANGE)
        elif action == Action.DOWN:
            begin = (pos[0] - self._RANGE, pos[1] - self._RANGE)
            end = (pos[0] + self._RANGE, pos[1])
        else:
            return Strategy.MAX_ACTION_LVL

        total, wall = 1, 1
        for x in range(begin[0], end[0]):
            for y in range(begin[1], end[1]):
                total += 1
                if not self._role.map.valid(x, y) or (self._role.revealed((x, y)) and self._role.map.wall(x, y)):
                    wall += 1
        return round(wall / total, 2)


class AStar(Strategy):
    """
    A* path-finding.
    """
    @staticmethod
    def name() -> str:
        return "aStar"

    def __init__(self, role: 'gr.Role') -> None:
        super().__init__(role)
        self._prev_path: list[_Spot] = []

        spots = [[None] * role.map.height for _ in range(role.map.width)]
        for x in range(role.map.width):
            for y in range(role.map.height):
                spots[x][y] = _Spot(x, y)
        self._grid: Grid = Grid(spots)
        self._init_neighbors()

    @property
    def prev_path(self) -> list[tuple[int, int]]:
        """
        Get the previous path.
        """
        return [spot.pos for spot in self._prev_path]

    def action_lvls(self, status: 'gm.Status') -> ActionLevels:
        lvls = self.new_init_lvls()
        self._prev_path = self._path(status)
        if len(self._prev_path) > 0:
            action = Action.next(self._role.pos, self._prev_path[1].pos)
            lvls[action] = Strategy.MAX_ACTION_LVL
        return lvls

    def _path(self, status: 'gm.Status') -> list[_Spot]:
        """
        Find a path to the opponent.
        """
        self._clear_spots()
        heuristic = cfg.heuristic
        open_set, closed_set = [], []

        def next_pos() -> _Spot:
            assert len(open_set) > 0
            pos = min(open_set, key=lambda s: s.f)
            open_set.remove(pos)
            return pos

        src = self._role.pos
        dest = status.opponent(self._role).pos
        open_set.append(self._grid.spot(*src))
        while len(open_set) > 0:
            spot = next_pos()
            if spot.pos == dest:
                return spot.retrace()
            closed_set.append(spot)

            for neighbor in self._grid.neighbors(*spot.pos):
                if neighbor in closed_set:
                    continue
                new_g = spot.g + heuristic(spot.pos, neighbor.pos)
                if self._role.revealed(neighbor.pos):
                    if self._role.map.wall(*neighbor.pos):
                        self._grid.delete(*neighbor.pos)
                        continue
                    else:
                        new_g += self._role.map.move_cost(*neighbor.pos)
                else:
                    new_g += cfg.move_cost["grass"]

                new_path = False
                if neighbor in open_set:
                    if new_g < neighbor.g:
                        neighbor.g = new_g
                        new_path = True
                else:
                    neighbor.g = new_g
                    new_path = True
                    open_set.append(neighbor)

                if new_path:
                    neighbor.g = new_g
                    neighbor.prev = spot
        return []

    def _init_neighbors(self) -> None:
        """
        Initialize the neighbors of each spot.
        """
        for x in range(self._role.map.width):
            for y in range(self._role.map.height):
                self._grid.spot(x, y).neighbors = self._grid.neighbors(x, y)

    def _clear_spots(self) -> None:
        """
        Clear the path-finding record.
        """
        for x in range(self._role.map.width):
            for y in range(self._role.map.height):
                if self._grid.valid(x, y):
                    self._grid.spot(x, y).clear()
