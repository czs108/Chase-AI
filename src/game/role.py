from collections.abc import Sequence

import game.map as gm
import game.strategy as sg
from game import cfg
from game.action import Action


class Role:
    """
    The game role.
    """
    def __init__(self, status: 'gm.Status', map: 'gm.Map', pos: tuple[int, int]) -> None:
        """
        The constructor.

        -- PARAMETERS --
        status: The game status.
        map: The game map.
        pos: The position of the role.
        """
        self._status: 'gm.Status' = status
        self._map: gm.Map = map

        # The current position.
        self._pos: tuple[int, int] = None

        # Whether a position has been discovered.
        self._revealed: list[list[bool]] = [[False] * map.height for _ in range(map.width)]

        # The previous destination the role tried to move to.
        self._prev_try_pos: tuple[int, int] = None

        # Whether the previous action failed because of a wall.
        self._wall_blocked: bool = False

        # Whether the role is trapped in a bush.
        self._bush_trapped: bool = False

        # The action strategy chain and selector.
        self._selector: sg.ActionSelector = None
        self._strategies: list[sg.Strategy] = []

        assert map.occupied(*pos, status) == gm.Occupy.NONE
        self._try_move(pos)
        self._reveal()

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @property
    def map(self) -> 'gm.Map':
        return self._map

    @property
    def strategy_weights(self) -> Sequence[float]:
        return self._selector.weights

    @strategy_weights.setter
    def strategy_weights(self, value: Sequence[float]) -> None:
        self._selector.weights = value

    def revealed(self, pos: tuple[int, int]) -> bool:
        """
        Reveal a new position, which means the role has known its terrain.
        """
        return self._revealed[pos[0]][pos[1]]

    def move(self) -> bool:
        """
        Move one step.
        """
        action = self.peek_action()
        dest = action.dest(self._pos)
        ret = self._try_move(dest)
        self._reveal()
        return ret

    def peek_action(self) -> Action:
        """
        Choose the next action.
        """
        lvl_matrix = []
        for strategy in self._strategies:
            lvl_matrix.append(strategy.action_lvls(self._status))
        # Get the action with the highest level of recommendation.
        return self._selector.highest(lvl_matrix)

    def terrain(self) -> 'gm.Terrain':
        """
        Get the terrain of the role's position.
        """
        return self._map.terrain(*self._pos)

    def stuck(self) -> bool:
        """
        Check whether the role is stuck.
        """
        for action in Action:
            dest = action.dest(self._pos)
            if self._map.occupied(*dest, self._status) == gm.Occupy.NONE:
                return False
        return True

    def _reveal(self) -> None:
        """
        Update terrains.
        """
        x, y = self._pos
        self._revealed[x][y] = True
        if self._wall_blocked:
            prev_x, prev_y = self._prev_try_pos
            self._revealed[prev_x][prev_y] = True

    def _try_move(self, pos: tuple[int, int]) -> bool:
        """
        Try to move to the destination.
        """
        self._prev_try_pos = pos
        self._wall_blocked = False
        if self._pos == pos:
            return True
        elif self._bush_trapped:
            # Lost this turn because of being trapped.
            self._bush_trapped = False
            return False

        occupy = self._map.occupied(*pos, self._status)
        if occupy != gm.Occupy.NONE:
            self._wall_blocked = occupy == gm.Occupy.WALL
            return False
        else:
            self._pos = pos
            self._bush_trapped = self._map.terrain(*pos) == gm.Terrain.BUSH
            return True


class Agent(Role):
    def __init__(self, status: 'gm.Status', map: 'gm.Map', pos: tuple[int, int]) -> None:
        super().__init__(status, map, pos)
        self._revealed = [[True] * map.height for _ in range(map.width)]
        self._load_strategies()

    def _reveal(self) -> None:
        pass

    def _load_strategies(self) -> None:
        weights = []
        for s, w in cfg.strategy_weights("agent").items():
            if w < 0:
                raise ValueError("Invalid strategy weight.")
            elif w == 0:
                continue

            if s == sg.Random.name():
                self._strategies.append(sg.Random(self))
            elif s == sg.MoveAway.name():
                self._strategies.append(sg.MoveAway(self))
            elif s == sg.MoveClose.name():
                self._strategies.append(sg.MoveClose(self))
            elif s == sg.WallDensity.name():
                self._strategies.append(sg.WallDensity(self))
            else:
                raise ValueError("Invalid action strategy.")
            weights.append(w)

        if len(self._strategies) == 0:
            self._strategies.append(sg.Random(self))
            weights = [1]
        self._selector = sg.ActionSelector(weights)


class Enemy(Role):
    def __init__(self, status: 'gm.Status', map: 'gm.Map', pos: tuple[int, int]) -> None:
        super().__init__(status, map, pos)
        self._a_star: sg.AStar = None
        self._load_strategies()

    @property
    def path(self) -> list[tuple[int, int]]:
        """
        Get the A* path if it exists.
        """
        if not self._a_star:
            return []
        prev_path = self._a_star.prev_path
        try:
            begin = prev_path.index(self._pos)
            path = prev_path[begin:]
            return path
        except ValueError:
            return []

    def _load_strategies(self) -> None:
        weights = []
        for s, w in cfg.strategy_weights("enemy").items():
            if w < 0:
                raise ValueError("Invalid strategy weight.")
            elif w == 0:
                continue

            if s == sg.Random.name():
                self._strategies.append(sg.Random(self))
            elif s == sg.MoveAway.name():
                self._strategies.append(sg.MoveAway(self))
            elif s == sg.MoveClose.name():
                self._strategies.append(sg.MoveClose(self))
            elif s == sg.WallDensity.name():
                self._strategies.append(sg.WallDensity(self))
            elif s == sg.AStar.name():
                self._a_star = sg.AStar(self)
                self._strategies.append(self._a_star)
            else:
                raise ValueError("Invalid action strategy.")
            weights.append(w)

        if len(self._strategies) == 0:
            self._strategies.append(sg.Random(self))
            weights = [1]
        self._selector = sg.ActionSelector(weights)
