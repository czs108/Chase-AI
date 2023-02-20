class Spot {
    #pos;
    #neighbors = [];

    #g = 0;
    #h = 0;

    previous = null;

    constructor(pos) {
        this.#pos = pos;
    }

    addNeighbors(grid, maze, diagonalMove) {
        const neighbors = this.#neighbors;

        const { x, y } = this.#pos;
        if (maze.valid({ x, y: y - 1 }) && !maze.wall({ x, y: y - 1 })) {
            neighbors.push(grid[x][y - 1]);
        }
        if (maze.valid({ x, y: y + 1 }) && !maze.wall({ x, y: y + 1 })) {
            neighbors.push(grid[x][y + 1]);
        }
        if (maze.valid({ x: x - 1, y }) && !maze.wall({ x: x - 1, y })) {
            neighbors.push(grid[x - 1][y]);
        }
        if (maze.valid({ x: x + 1, y }) && !maze.wall({ x: x + 1, y })) {
            neighbors.push(grid[x + 1][y]);
        }

        if (diagonalMove) {
            if (maze.valid({ x: x - 1, y: y - 1 }) && !maze.wall({ x: x - 1, y: y - 1 })) {
                neighbors.push(grid[x - 1][y - 1]);
            }
            if (maze.valid({ x: x + 1, y: y - 1 }) && !maze.wall({ x: x + 1, y: y - 1 })) {
                neighbors.push(grid[x + 1][y - 1]);
            }
            if (maze.valid({ x: x - 1, y: y + 1 }) && !maze.wall({ x: x - 1, y: y + 1 })) {
                neighbors.push(grid[x - 1][y + 1]);
            }
            if (maze.valid({ x: x + 1, y: y + 1 }) && !maze.wall({ x: x + 1, y: y + 1 })) {
                neighbors.push(grid[x + 1][y + 1]);
            }
        }
    }

    get neighbors() {
        return this.#neighbors;
    }

    get pos() {
        return this.#pos;
    }

    get y() {
        return this.#pos.y;
    }

    get x() {
        return this.#pos.x;
    }

    get g() {
        return this.#g;
    }

    set g(val) {
        this.#g = val;
    }

    get h() {
        return this.#h;
    }

    set h(val) {
        this.#h = val;
    }

    get f() {
        return this.#g + this.#h;
    }
}