class Displayer {
    #searcher
    #cellSize;
    #color;

    constructor(canvasSize, color, searcher) {
        this.#searcher = searcher;
        this.#color = color;
        this.#cellSize = {
            width: canvasSize.width / (searcher.maze.width + 1),
            height: canvasSize.height / (searcher.maze.height + 1)
        };
    }

    showMaze() {
        this.#showBorder();

        const maze = this.#searcher.maze;
        for (let x = 0; x < maze.width; x++) {
            for (let y = 0; y < maze.height; y++) {
                if (maze.wall({ x, y })) {
                    fill('black');
                } else {
                    fill('white');
                }

                this.#showGrid({ x, y });
            }
        }

        this.#showStartEnd();
    }

    showClosedSet() {
        const closedSet = this.#searcher.closedSet;
        fill(this.#color.search.closed);
        for (let i = 0; i < closedSet.length; i++) {
            this.#showGrid(closedSet[i]);
        }

        this.#showStartEnd();
    }

    showOpenSet() {
        const openSet = this.#searcher.openSet;
        fill(this.#color.search.open);
        for (let i = 0; i < openSet.length; i++) {
            this.#showGrid(openSet[i]);
        }

        this.#showStartEnd();
    }

    showPath() {
        noFill();
        stroke(this.#color.search.path);
        const { width, height } = this.#cellSize;
        const length = Math.min(width, height);
        strokeWeight(length / 8);
        beginShape();
        const path = this.#searcher.path;
        for (let i = 0; i < path.length; i++) {
            vertex((path[i].x * width) + width / 2,
                (path[i].y * height) + height / 2);
        }
        endShape();
    }

    #showBorder() {
        fill('black');
        const maze = this.#searcher.maze;
        for (let x = 0; x <= maze.width; x++) {
            this.#showGrid({ x, y: maze.height });
        }

        for (let y = 0; y <= maze.height; y++) {
            this.#showGrid({ x: maze.width, y });
        }
    }

    #showStartEnd() {
        const maze = this.#searcher.maze;
        this.#showPoint(maze.start, this.#color.maze.startEnd);
        this.#showPoint(maze.end, this.#color.maze.startEnd);
    }

    #showPoint({ x, y }, color) {
        stroke(color);
        const { width, height } = this.#cellSize;
        const length = Math.min(width, height);
        strokeWeight(length / 1.5);
        point(x * width + width / 2, y * height + height / 2);
    }

    #showGrid({ x, y }) {
        stroke('white');
        strokeWeight(1);
        const { width, height } = this.#cellSize;
        rect(x * width, y * height, width, height);
    }
}