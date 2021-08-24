# Chase AI

[![Python](badges/Python-3.10.svg)](https://www.python.org)
![ECMAScript](badges/ECMAScript-6.svg)
[![License](badges/License-GPL-3.0.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![DOI](https://zenodo.org/badge/330611245.svg)](https://zenodo.org/badge/latestdoi/330611245)

## About The Project

![Cover](../Cover.png)

An artificial intelligence game to demonstrate the ***A\* pathfinding***. The enemy will try to get close to the agent and make it stuck between walls.

## Getting Started

### Prerequisites

- Install [*Python 3.10*](https://www.python.org).

- Install all dependencies.

  ```bash
  pip install -r requirements.txt
  ```

### Running

```bash
python main.py
```

### Configurations

The game configuration is in the `src/config.json` file. There are some important options.

- The probability (density) of different terrains.

  ```json
  "terrainProb": {
      "wall": 0.25,
      "bush": 0.2
  },
  ```

- The move cost of different terrains.

  ```json
  "moveCost": {
      "grass": 1,
      "bush": 10
  },
  ```

- The strategy weight for different roles.

  ```json
  "strategyWeights": {
      "agent": {
          "random": 1
      },

      "enemy": {
          "random": 0.2,
          "moveClose": 0.3,
          "aStar": 1
      }
  }
  ```

## Terrains

There are three kinds of terrains: ***grass***, ***bush***, ***wall***. They have different move costs and features.

- *Grass*

  ![grass](../src/res/grass.png)

  A grass tile has 1 unit of move cost by default.

- *Bush*

  ![bush](../src/res/bush.png)

  A bush tile has 10 units of move cost by default.

  If a role moves onto a bush tile, it will be trapped and ***lose the next move chance***.

- *Wall*

  ![stone-wall](../src/res/stone-wall.png)

  ![wooden-wall](../src/res/wooden-wall.png)

  A wall tile cannot be passed through.

When a role moves, it will consider the cost of different terrains and avoid bushes, as the *blue* path shows.

![avoid-bush](images/avoid-bush.png)

### Black Fog

At first, the enemy knows *nothing* about terrains except its current position. The terrain of the complete map will be displayed according to the enemy's exploration. Unknown tiles are displayed as below:

![plain](../src/res/plain.png)

The movement might fail because of occupation or invalid positions. The enemy can get the cause of failure and ***memorize terrains***. Some action strategies can use terrain information.

```python
class Occupy(Enum):
    # No occupation.
    NONE = auto()
    # The position is invalid.
    INVALID = auto()
    # The position is a wall.
    WALL = auto()
    # The position is occupied by a role.
    ROLE = auto()
```

## Strategies

It's a key design to a role's behavior. A `Strategy` is a kind of logic to determine the ***next action*** according to the game status.

![strategy-uml](images/strategy-uml.png)

The `name` method returns the strategy name used in the `src/config.json` file.

The `action_lvls` method returns an array containing the level of recommendation for every action.

Assume:

![action-level](images/action-level.png)

Then `action_lvls` returns:

![action-vector](images/action-vector.png)

I have implemented five kinds of strategies. They can be ***combined*** together.

### Random Move

`Random` is the default strategy. All valid actions except *stay* will get ***random*** recommendation levels.

### Move Away & Move Close

`MoveAway` and `MoveClose` only consider the ***next one step***. They use the following estimate function to maximize or minimize the distance between the agent and enemy.

```python
def dist(src: tuple[int, int], dest: tuple[int, int]) -> float:
    return abs(src[0] - dest[0]) + abs(src[1] - dest[1])
```

### Wall Density

`WallDensity` tries to find a direction where the ***density*** of walls is lower.

![wall-density](images/wall-density.png)

### A* Search

`AStar` tries to find the shortest path from the enemy to the agent, as the *blue* path shows.

At first, the enemy knows nothing about terrains, so `AStar` assumes that all tiles are ***grass*** and finds an ***ideal*** path.

![beginning](images/beginning.png)

After the enemy learns terrains from its movements, `AStar` will become more accurate.

## Strategy Weights

A role can combine more than one strategy and the importance of each strategy is represented by its ***weight***. The role uses *weighted addition* to get the final action.

Assume:

![strategy-weight](images/strategy-weight.png)

Then the final level of recommendation for each action is:

![weighted-addition](images/weighted-addition.png)

The role will choose the action with the ***highest*** value.

## Test Statistics

All tests have the following fixed options:

```json
"maxSteps": 500,

"mapSize": {
    "height": {
        "min": 25,
        "max": 25
    },

    "width": {
        "min": 25,
        "max": 25
    }
},

"terrainProb": {
    "wall": 0.3,
    "bush": 0.1
},

"moveCost": {
    "grass": 1,
    "bush": 15
},
```

And the agent and enemy will be randomly generated in the left half and right half of the map.

### The Agent

When testing the agent, the enemy's strategy weights are fixed as below:

```json
"enemy": {
    "random": 0.1,
    "aStar": 1,
    "moveClose": 0.2,
    "wallDensity": 0.1
}
```

The agent's strategy weights are changed in each trial.

| Test ID |                Strategy Weights                 |
| :-----: | :---------------------------------------------: |
|    1    |                    [1, 0, 0]                    |
|    2    |                    [1, 1, 1]                    |
|    3    | [1, 0 ~ 0.4, 0 ~ 0.4]. It changes in each step. |
|    4    |   [1, 0 ~ 1, 0 ~ 1]. It changes in each step.   |

> The order of weights is `Random`, `MoveAway`, `WallDensity`.

The game runs 100 times in each trial and the agent's scores are shown below:

![agent-test](images/agent-test.png)

### The Enemy

When testing the enemy, the agent's strategy weights are fixed.

```json
"agent": {
    "random": 0.1,
    "moveAway": 0.4,
    "wallDensity": 0.4
}
```

The enemy's strategy weights are changed in each trial.

| Test ID |  Strategy Weights  |
| :-----: | :----------------: |
|    1    |    [1, 0, 0, 0]    |
|    2    | [0.5, 0, 0.7, 0.9] |
|    3    |    [0, 1, 0, 0]    |
|    4    | [0.1, 1, 0.2, 0.1] |

> The order of weights is `Random`, `AStar`, `MoveClose`, `WallDensity`.

The game runs 100 times in each trial and the agent's scores are shown below:

![enemy-test](images/enemy-test.png)

## Dependencies

[*pygame*](https://www.pygame.org)

## License

Distributed under the *GNU General Public License*. See `LICENSE` for more information.

The image resources are from the book "*Making Games with Python & Pygame*" written by *Al Sweigart*.

## Citing

```tex
@software{chenzs108_2021_4698338,
  author       = {Chenzs108},
  title        = {czs108/Chase-AI: v1.0.0},
  month        = apr,
  year         = 2021,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.4698338},
  url          = {https://doi.org/10.5281/zenodo.4698338}
}
```

## Contact

***GitHub***: https://github.com/czs108

***E-Mail***: chenzs108@outlook.com

***WeChat***: chenzs108