import { useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
// import images
import b_bishop from './assets/b-bishop.svg';
import b_knight from './assets/b-knight.svg';
import b_king from './assets/b-king.svg';
import b_pawn from './assets/b-pawn.svg';
import b_queen from './assets/b-queen.svg';
import b_rook from './assets/b-rook.svg';
import w_bishop from './assets/w-bishop.svg';
import w_knight from './assets/w-knight.svg';
import w_king from './assets/w-king.svg';
import w_pawn from './assets/w-pawn.svg';
import w_queen from './assets/w-queen.svg';
import w_rook from './assets/w-rook.svg';
import fog from './assets/fog.svg';

// maps char -> image
const imageMap = {
    'K': w_king,
    'Q': w_queen,
    'R': w_rook,
    'B': w_bishop,
    'N': w_knight,
    'P': w_pawn,
    'k': b_king,
    'q': b_queen,
    'r': b_rook,
    'b': b_bishop,
    'n': b_knight,
    'p': b_pawn,
    'f': fog,
    '.': undefined,
}

const Sides = Object.freeze({
    WHITE: 1,
    BLACK: 0,
});

const white_pieces = new Set(['K', 'Q', 'R', 'B', 'N', 'P']);
const black_pieces = new Set(['k', 'q', 'r', 'b', 'n', 'p']);

export default function Game() {
    const location = useLocation();
    // location stores stuff passed from Main.jsx
    const { game_id, visual: initialVisual, legal_moves, client_side } = location.state || {};

    // visual is a 5x5 of what we can see
    const [visual, setVisual] = useState(initialVisual);
    // legal moves is an arr of  [[i, j], [dx, dy], promotion]
    // where i, j is the square, dx, dy is used to calc the position of where to move, ...
    const [legalMoves, setLegalMoves] = useState(legal_moves);
    // format [i, j]
    const [selectedSquare, setSelectedSquare] = useState(null);

    // runs when square is clicked
    function handleClick(i, j) {
        const pieces_set = client_side == Sides.WHITE ? white_pieces : black_pieces;
        // clicking on our piece
        if (pieces_set.has(visual[i][j])) {
            if (!selectedSquare) {
                setSelectedSquare([i, j]);
            } else {
                const [si, sj] = selectedSquare;
                if (si == i && sj == j) {
                    // unselecting
                    setSelectedSquare(null);
                } else {
                    // selecting
                    setSelectedSquare([i, j]);
                }
            }
        }
    }

    // list of moves [i,j] that our currentl;y selected piece can make
    let selectedMoves = [];
    if (selectedSquare) {
        const [i, j] = selectedSquare;
        selectedMoves = legalMoves.filter(move => move[0][0] == i && move[0][1] == j)
            .map(move => [move[0][0] + move[1][0], move[0][1] + move[1][1]]);
    }
    console.log('selectedMoves', selectedMoves);

    return (
        <div className='h-screen bg-gray-950 flex items-center justify-center text-white'>
            {/* <div className={`h-3/4 aspect-square bg-gray-950 flex flex-col overflow-y-auto
                justify-evenly items-center border-2 p-10 text-center`}>

            </div> */}
            <div className="grid grid-cols-5 grid-rows-5 h-3/4 aspect-square border-2 border-gray-300">
                {visual.map((row, i) =>
                    row.map((piece, j) => (
                        <ChessSquare
                            key={`${i}-${j}`}
                            i={i}
                            j={j}
                            visual={visual}
                            handleClick={handleClick}
                            selectedSquare={selectedSquare}
                            selectedMoves={selectedMoves} />
                    ))
                )}
            </div>
        </div>
    );
}

// a chess square
function ChessSquare({ i, j, visual, handleClick, selectedSquare, selectedMoves }) {
    const piece = visual[i][j];
    let color = (i + j) % 2 == 0 ? 'bg-amber-100' : 'bg-amber-800';
    let image = imageMap[piece];
    let has_fog = piece == 'f';
    // this is a fog square
    if (has_fog) {
        color = 'bg-gray-800';
        has_fog = true;
        image = fog;
    }
    // determine if we highlight this square
    if (selectedSquare && selectedSquare[0] == i && selectedSquare[1] == j) {
        color = 'bg-yellow-300';
    }
    // need custom search since .includes[i,j] doesnt work \
    // arrs are objects, and objects are compared by reference
    const in_selected_moves = selectedMoves.some(move => move[0] == i && move[1] == j);
    return (
        <div className={`relative w-full h-full ${has_fog ? 'p-10' : 'p-4'} ${color}
            flex items-center justify-center` }
            onClick={() => handleClick(i, j)}>
            {image && <img src={image} className='w-full h-full' alt={piece} />}
            {in_selected_moves &&
                <div className='absolute w-1/3 aspect-square bg-gray-500/80 rounded-full' >
                </div>}
        </div>
    )
}
