class Maze {
    #size;
    #wall;

    #start;
    #end;

    constructor({ width, height }, { start, end }, wallThreshold) {
        this.#size = { width, height };
        this.#start = start;
        this.#end = end;
        this.#wall = new Array(width);
        for (let x = 0; x < width; x++) {
            this.#wall[x] = new Array(height);
            for (let y = 0; y < height; y++) {
                this.#wall[x][y] = Math.random() < wallThreshold ? true : false;
            }
        }

        this.#wall[start.x][start.y] = false;
        this.#wall[end.x][end.y] = false;
    }

    get width() {
        return this.#size.width;
    }

    get height() {
        return this.#size.height;
    }

    get start() {
        return this.#start;
    }

    get end() {
        return this.#end;
    }

    wall({ x, y }) {
        return this.#wall[x][y];
    }

    valid({ x, y }) {
        const validRow = 0 <= y && y < this.height;
        const validCol = 0 <= x && x < this.width;
        return validRow && validCol;
    }
}