/**
 * Basic configurations.
 */
const CONFIG = {

    //! Whether diagonal move is allowed.
    diagonalMove: true,

    //! The probability of generating a wall.
    wallThreshold: 0.3,

    /**
     * The estimate function.
     *
     * @warning It must be always optimistic - real time will be this or longer.
     */
    heuristic: (src, dest) => {
        if (this.diagonalMove) {
            return dist(src.x, src.y, dest.x, dest.y);
        } else {
            return Math.abs(src.x - dest.x) + Math.abs(src.y - dest.y);
        }
    },

    //! Use a slower frame rate to see how it is working.
    //! e.g. 2 or 5;
    frameRate: null
};

const COLOR = {
    search: {
        open: 'lightgreen',
        closed: 'lightpink',
        path: 'darkred'
    },

    maze: {
        startEnd: 'blue'
    }
};

// Canvas size.
const CANVAS_WIDTH = 900;
const CANVAS_HEIGHT = 600;

// Number of columns and rows.
const gridBase = randomInt(2, 8);
const colNum = 9 * gridBase;
const rowNum = 6 * gridBase;


let searcher;
let displayer;

function setup() {
    if (CONFIG.frameRate) {
        frameRate(CONFIG.frameRate);
    }

    const start = { x: 0, y: randomInt(0, rowNum - 1) };
    const end = { x: colNum - 1, y: randomInt(0, rowNum - 1) };
    const maze = new Maze({ width: colNum, height: rowNum }, { start, end }, CONFIG.wallThreshold);
    searcher = new Searcher(maze, CONFIG.diagonalMove, CONFIG.heuristic);

    createCanvas(CANVAS_WIDTH, CANVAS_HEIGHT);
    displayer = new Displayer({ width: CANVAS_WIDTH, height: CANVAS_HEIGHT }, COLOR, searcher);
}

function draw() {
    background('white');
    displayer.showMaze();

    const end = searcher.nextPath();
    displayer.showClosedSet();
    displayer.showOpenSet();
    displayer.showPath();
    if (end) {
        noLoop();
    }
}

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}