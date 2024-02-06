# Chase AI

[![Python](badges/Python.svg)](https://www.python.org)
![ECMAScript](badges/ECMAScript.svg)
![License](badges/License-MIT.svg)

## Introduction

![Cover](../Cover.gif)

An artificial intelligence game to demonstrate the ***A\* path-finding***. The enemy will try to get close to the agent and make it stuck between walls.

## Getting Started

### Prerequisites

- Install [*Python 3.11*](https://www.python.org).

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

## Class Diagram

```mermaid
classDiagram

class Action {
    <<enumeration>>
    Stay
    Up
    Down
    Left
    Right
}

class Occupy {
    <<enumeration>>
    None
    Wall
    Role
}

class Terrain {
    <<enumeration>>
    Wall
    Grass
    Bush
}

class Status {
    int score
    int steps
    Agent agent
    Enemy enemy
}

class Map {
    terrain(x, y) Terrain
    occupied(x, y, Status) Occupy
    move_cost(x, y) float
}

Map ..> Status
Map ..> Occupy
Map *-- Terrain

class Role {
    <<abstract>>
    move() bool
    peek_action() Action
    stuck() bool
}

Role ..> Action
Role --> Map
Role -- Status

class Agent
Role <|-- Agent

class Enemy {
    list~pos~ path
}

Role <|-- Enemy

class ActionLevels {
    dict~Action, float~ weights
}

ActionLevels --> Action

class Strategy {
    <<abstract>>
    action_lvls(Status)* ActionLevels
}

Strategy ..> ActionLevels
Strategy ..> Status
Strategy --> Role

class Random
Strategy <|-- Random

class MoveAway
Strategy <|-- MoveAway

class MoveClose
Strategy <|-- MoveClose

class WallDensity
Strategy <|-- WallDensity

class AStar {
    list~pos~ prev_path
}

Strategy <|-- AStar

Enemy --> Random
Enemy --> AStar
Enemy --> MoveClose
Enemy --> WallDensity

Agent --> Random
Agent --> MoveAway
Agent --> WallDensity
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

- [*pygame*](https://www.pygame.org)

## License

Distributed under the *MIT License*. See `LICENSE` for more information.

The image resources are from the book "*Making Games with Python & Pygame*" written by *Al Sweigart*.