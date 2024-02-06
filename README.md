# Chase AI

[![Python](docs/badges/Python.svg)](https://www.python.org)
![ECMAScript](docs/badges/ECMAScript.svg)
![License](docs/badges/License-MIT.svg)

## Introduction

![Cover](Cover.gif)

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

The game configuration is in the `src/config.json` file.

## Documents

See `docs/wiki.md` for the details.

### Class Diagram

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

## Dependencies

- [*pygame*](https://www.pygame.org)

## License

Distributed under the *MIT License*. See `LICENSE` for more information.

The image resources are from the book "*Making Games with Python & Pygame*" written by *Al Sweigart*.
