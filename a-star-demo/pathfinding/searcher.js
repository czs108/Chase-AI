class Searcher {
    #maze;
    #memo;
    #heuristic = (src, dest) => 0;

    #pos;
    #path;
    #openSet = [];
    #closedSet = [];

    constructor(maze, diagonalMove, heuristic) {
        this.#maze = maze;
        if (heuristic) {
            this.#heuristic = heuristic;
        }

        this.#initMemo(maze, diagonalMove);
        this.openSet.push(this.#memo[maze.start.x][maze.start.y]);
    }

    get openSet() {
        return this.#openSet;
    }

    get closedSet() {
        return this.#closedSet;
    }

    get path() {
        return this.#path;
    }

    get pos() {
        return this.#pos;
    }

    get maze() {
        return this.#maze;
    }

    nextPath() {
        if (this.openSet.length > 0) {
            this.#pos = this.#nextPos();
            this.closedSet.push(this.#pos);

            const neighbors = this.#pos.neighbors;
            for (let i = 0; i < neighbors.length; i++) {
                const neighbor = neighbors[i];
                if (!this.closedSet.includes(neighbor)) {
                    const newG = this.#pos.g + this.#heuristic(neighbor, this.#pos);

                    let newPath = false;
                    if (this.openSet.includes(neighbor)) {
                        if (newG < neighbor.g) {
                            neighbor.g = newG;
                            newPath = true;
                        }
                    } else {
                        neighbor.g = newG;
                        newPath = true;
                        this.openSet.push(neighbor);
                    }

                    if (newPath) {
                        neighbor.h = this.#heuristic(neighbor, this.#maze.end);
                        neighbor.previous = this.#pos;
                    }
                }
            }

            this.#path = Searcher.#trackPath(this.#pos);
            return this.#end();

        } else {
            this.#path = null;
            return false;
        }
    }

    #nextPos() {
        let next = 0;
        for (let i = 1; i < this.openSet.length; i++) {
            if (this.openSet[i].f < this.openSet[next].f) {
                next = i;
            }
        }

        const pos = this.openSet[next];
        this.openSet.splice(next, 1);
        return pos;
    }

    #end() {
        const { x: endX, y: endY } = this.#maze.end;
        return this.#pos.x === endX && this.#pos.y === endY;
    }

    #initMemo(maze, diagonalMove) {
        this.#memo = new Array(maze.width);
        for (let x = 0; x < maze.width; x++) {
            this.#memo[x] = new Array(maze.height);
            for (let y = 0; y < maze.height; y++) {
                if (!maze.wall({ x, y })) {
                    this.#memo[x][y] = new Spot({ x, y });
                }
            }
        }

        for (let x = 0; x < maze.width; x++) {
            for (let y = 0; y < maze.height; y++) {
                if (!maze.wall({ x, y })) {
                    this.#memo[x][y].addNeighbors(this.#memo, maze, diagonalMove);
                }
            }
        }
    }

    static #trackPath(spot) {
        let path = [];
        let curr = spot;
        path.push(curr);
        while (curr.previous) {
            path.push(curr.previous);
            curr = curr.previous;
        }

        return path;
    }
}