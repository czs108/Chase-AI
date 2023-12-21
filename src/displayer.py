from pathlib import Path
from random import randint
from collections.abc import Sequence

import pygame as pg

from game.map import Map, Status, Terrain
from game import cfg


class Displayer:
    """
    Display the game.
    """
    _TILE_WIDTH: int = 50
    _TILE_HEIGHT: int = 85
    _TILE_FLOOR_HEIGHT: int = 40

    _BG_COLOR: tuple[int, int, int] = (0, 170, 255)

    def __init__(self) -> None:
        self._map: Map = None
        self._status: Status = None

        # The size of the window.
        self._width: int = 0
        self._height: int = 0
        self._window: pg.Surface = None

        self._fps_clock: pg.time.Clock = pg.time.Clock()
        self._fps: int = cfg.fps
        if self._fps <= 0:
            raise ValueError("Invalid FPS.")

        self._images: dict[str, pg.image] = self._load_images(Path(__file__).parent.joinpath("res"))
        self._enemy_image: pg.image = None
        self._ground_images: list[list[pg.image]] = None

    def init(self, map: Map, status: Status) -> 'Displayer':
        self._map = map
        self._status = status
        self._width = map.width * self._TILE_WIDTH
        self._height = (map.height - 1) * self._TILE_FLOOR_HEIGHT + self._TILE_HEIGHT
        self._window = pg.display.set_mode((self._width, self._height))

        walls = (self._images["wooden wall"], self._images["stone wall"])
        enemies = (self._images["boy"], self._images["cat girl"], self._images["horn girl"],
                   self._images["pink girl"], self._images["princess"])

        def random_image(images: Sequence[pg.image]) -> pg.image:
            """
            Get a random image.
            """
            assert len(images) > 0
            return images[randint(0, len(images) - 1)]

        self._enemy_image = random_image(enemies)
        self._ground_images = [[None] * map.height for _ in range(map.width)]
        for x in range(map.width):
            for y in range(map.height):
                if map.terrain(x, y) == Terrain.WALL:
                    self._ground_images[x][y] = random_image(walls)
                else:
                    self._ground_images[x][y] = self._images["grass"]
        return self

    def update(self) -> None:
        self._window.fill(self._BG_COLOR)
        self._draw_map()
        pg.display.update()
        self._fps_clock.tick(self._fps)

    def _draw_map(self) -> None:
        path = set(self._status.enemy.path) if len(self._status.enemy.path) > 0 else set()
        map_surf = pg.Surface((self._width, self._height))
        map_surf.fill(self._BG_COLOR)
        for x in range(self._map.width):
            for y in range(self._map.height):
                rect = pg.Rect((x * self._TILE_WIDTH, y * self._TILE_FLOOR_HEIGHT,
                                self._TILE_WIDTH, self._TILE_HEIGHT))
                if self._status.game_end or self._status.enemy.revealed((x, y)):
                    # The position has been discovered.
                    if (x, y) in path and self._map.terrain(x, y) != Terrain.WALL:
                        # Show the path from the enemy to the agent.
                        map_surf.blit(self._images["grass path"], rect)
                    else:
                        map_surf.blit(self._ground_images[x][y], rect)

                    if self._map.terrain(x, y) == Terrain.BUSH:
                        # Show bushes.
                        map_surf.blit(self._images["bush"], rect)
                else:
                    # Show black fog.
                    if (x, y) in path:
                        map_surf.blit(self._images["plain path"], rect)
                    else:
                        map_surf.blit(self._images["plain"], rect)

                # Show roles.
                if self._status.agent.pos == (x, y):
                    map_surf.blit(self._images["agent"], rect)
                elif self._status.enemy.pos == (x, y):
                    map_surf.blit(self._enemy_image, rect)
        self._window.blit(map_surf, map_surf.get_rect())

    @staticmethod
    def _load_images(path: Path) -> dict[str, pg.image]:
        return {
            # Agent.
            "agent": pg.image.load(str(path.joinpath("star.png"))),

            # Enemies.
            "boy": pg.image.load(str(path.joinpath("boy.png"))),
            "cat girl": pg.image.load(str(path.joinpath("cat-girl.png"))),
            "horn girl": pg.image.load(str(path.joinpath("horn-girl.png"))),
            "pink girl": pg.image.load(str(path.joinpath("pink-girl.png"))),
            "princess": pg.image.load(str(path.joinpath("princess.png"))),

            # Terrains.
            "plain": pg.image.load(str(path.joinpath("plain.png"))),
            "grass": pg.image.load(str(path.joinpath("grass.png"))),
            "plain path": pg.image.load(str(path.joinpath("plain-path.png"))),
            "grass path": pg.image.load(str(path.joinpath("grass-path.png"))),
            "bush": pg.image.load(str(path.joinpath("bush.png"))),
            "stone wall": pg.image.load(str(path.joinpath("stone-wall.png"))),
            "wooden wall": pg.image.load(str(path.joinpath("wooden-wall.png")))
        }
