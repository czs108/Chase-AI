import logging
import sys
from random import randint

import pygame as pg
from pygame.locals import *

from game import cfg
from game.map import Map, Status
from game.role import Agent, Enemy
from displayer import Displayer


def create_map() -> Map:
    map_size = cfg.map_size
    if not 1 < map_size["width"]["min"] <= map_size["width"]["max"] \
       or not 1 < map_size["height"]["min"] <= map_size["height"]["max"]:
        raise ValueError("Invalid size of map.")

    curr_try, max_try = 0, 100
    while curr_try < max_try:
        width = randint(map_size["width"]["min"], map_size["width"]["max"])
        height = randint(map_size["height"]["min"], map_size["height"]["max"])
        map = Map(width, height)
        if len(map.blanks()) >= 2:
            return map
        else:
            curr_try += 1
    raise RuntimeError(f"Failed to create a map containing at least 2 blanks within {max_try} times.")


def create_roles(status: Status, map: Map) -> None:
    blanks = map.blanks()
    assert len(blanks) >= 2

    def random_blank() -> tuple[int, int]:
        pos = blanks[randint(0, len(blanks) - 1)]
        blanks.remove(pos)
        return pos

    agent = Agent(status, map, random_blank())
    status.agent = agent
    enemy = Enemy(status, map, random_blank())
    status.enemy = enemy


def main():
    pg.init()
    pg.display.set_caption("Chase AI")
    status = Status()
    map = create_map()
    create_roles(status, map)
    displayer = Displayer().init(map, status)

    move_enemy = False
    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
        if not status.game_end:
            status.agent.move()
            if move_enemy:
                status.enemy.move()
            status.new_step()
            move_enemy = not move_enemy
            # The game will end if the agent is stuck or the number of steps reaches its maximum.
            if status.agent.stuck() or status.steps == cfg.max_steps:
                status.end_game()
                print(f"Agent Score: {status.score}")
        displayer.update()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    try:
        main()
    except SystemExit:
        pass
    except BaseException as err:
        logger.exception(err)
        sys.exit(1)
