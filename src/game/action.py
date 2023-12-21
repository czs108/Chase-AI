from enum import IntEnum
from random import randint


class Action(IntEnum):
    """
    The direction that a role can move to.
    """
    STAY = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def dest(self, src: tuple[int, int]) -> tuple[int, int]:
        """
        Get the destination after an action.
        """
        if self.value == Action.STAY:
            return src
        elif self.value == Action.UP:
            return src[0], src[1] + 1
        elif self.value == Action.DOWN:
            return src[0], src[1] - 1
        elif self.value == Action.LEFT:
            return src[0] - 1, src[1]
        elif self.value == Action.RIGHT:
            return src[0] + 1, src[1]
        else:
            assert False

    @staticmethod
    def next(src: tuple[int, int], dest: tuple[int, int]) -> 'Action':
        """
        Get the next action from the source to the destination.
        """
        def horizontal():
            if src[0] < dest[0]:
                return Action.RIGHT
            elif src[0] > dest[0]:
                return Action.LEFT
            else:
                return Action.STAY

        def vertical():
            if src[1] < dest[1]:
                return Action.UP
            elif src[1] > dest[1]:
                return Action.DOWN
            else:
                return Action.STAY

        actions = (horizontal(), vertical())
        if actions[0] == Action.STAY:
            return actions[1]
        elif actions[1] == Action.STAY:
            return actions[0]
        else:
            return actions[randint(0, 1)]
