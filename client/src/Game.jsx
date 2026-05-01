import { useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
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
import x from './assets/x.svg';
import arrow_back from './assets/arrow-back.svg';
import arrow_up from './assets/up-arrow.svg';
import arrow_down from './assets/down-arrow.svg';
// other stuff
import { url } from './App.jsx';

// maps char -> image
const image_map = {
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
// how server represents them
const BLACK = 0;
const WHITE = 1;

// maps piece -> how server represents it
const piece_map = {
    'K': 5,
    'k': 5,
    'Q': 4,
    'q': 4,
    'R': 3,
    'r': 3,
    'B': 2,
    'b': 2,
    'N': 1,
    'n': 1,
    'P': 0,
    'p': 0,
}

const white_pieces = new Set(['K', 'Q', 'R', 'B', 'N', 'P']);
const black_pieces = new Set(['k', 'q', 'r', 'b', 'n', 'p']);

const white_promo_pieces = ['R', 'B', 'N', 'Q'];
const black_promo_pieces = ['r', 'b', 'n', 'q'];

export default function Game() {
    const navigate = useNavigate();
    const location = useLocation();
    // location stores stuff passed from Main.jsx
    const { chess_game_id, visual: initialVisual, legal_moves, client_side, time } = location.state || {};
    // time between client moving and backend response
    const cooldown_ms = parseFloat(time) * 1000;
    // visual is a 5x5 of what we can see
    const [visual, setVisual] = useState(initialVisual);
    // legal moves is an arr of  [[i, j], [dx, dy], promotion]
    // where i, j is the square, dx, dy is used to calc the position of where to move, ...
    const [legalMoves, setLegalMoves] = useState(legal_moves);
    // format [i, j]
    const [selectedSquare, setSelectedSquare] = useState(null);
    // format [[i, j], [rowDiff, colDiff]]
    const [promotionInfo, setPromotionInfo] = useState(null);
    // 1 if client won, -1 if client lost, 0 if game is still going
    const [winStatus, setWinStatus] = useState(0);
    const [myTurn, setMyTurn] = useState(client_side == WHITE);

    const initialMoveMade = useRef(false);
    // check for server going first
    useEffect(() => {
        if (initialMoveMade.current) return;
        if (client_side == BLACK) {
            initialMoveMade.current = true;
            getServerMove();
        }
    }, []);

    // list of moves [i,j] that our currentl;y selected piece can make
    // auto updated according to selectedSquare's updates
    let selectedMoves = [];
    if (selectedSquare) {
        const [i, j] = selectedSquare;
        selectedMoves = legalMoves.filter(move => move[0][0] == i && move[0][1] == j)
            .map(move => [move[0][0] + move[1][0], move[0][1] + move[1][1]]);
    }

    // execute a move, expects move to be in format [[i, j], [dx, dy], promotion]
    async function executeMove(move) {
        console.log('move we are making', move);
        setSelectedSquare(null);
        setPromotionInfo(null);
        const [[i, j], [dx, dy], promotion] = move;
        const occupying_piece = visual[i][j];
        // visually update the board while waiting for server
        setVisual(old_visual => old_visual.map((row, oi) =>
            row.map((piece, oj) => {
                if (oi == i && oj == j) {
                    // old square is now empty
                    return '.';
                } else if (oi == dx && oj == dy) {
                    // new square is now occupied
                    return occupying_piece;
                } else {
                    return piece;
                }
            }
            )));
        const res = await fetch(`${url}/makeMove`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                move,
                chess_game_id
            }),
        });
        const resJSON = await res.json();
        const { visual: new_visual, legal_moves, is_game_over } = resJSON;
        setWinStatus(is_game_over);
        setVisual(old => new_visual);
        setLegalMoves(legal_moves);
        if (is_game_over != 0) {
            return;
        }
        // wait to make move
        await sleep(cooldown_ms);
        getServerMove();
    }

    // move the selectedSquare to dx, dy
    function processMove(dx, dy) {
        setMyTurn(false);
        const [i, j] = selectedSquare;
        // move back into format expected by backend
        const row_diff = dx - i;
        const col_diff = dy - j;
        const occupying_piece = visual[i][j];
        // pawn promotion
        if (occupying_piece.toLowerCase() == 'p' && (dx == 0 || dx == 4)) {
            setPromotionInfo(old => [[i, j], [row_diff, col_diff]]);
            return;
        }
        const move = [[i, j], [row_diff, col_diff], -1];
        executeMove(move);
    }

    // call server to get agent's move
    async function getServerMove() {
        const res = await fetch(`${url}/makesServerMove`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chess_game_id
            }),
        });
        const resJSON = await res.json();
        const { visual: new_visual, legal_moves, is_game_over } = resJSON;
        setWinStatus(is_game_over);
        setVisual(old => new_visual);
        setLegalMoves(legal_moves);
        if (is_game_over != 0) {
            return;
        }
        setMyTurn(true);
    }

    // runs when square is clicked
    function handleClick(i, j) {
        if (!myTurn) {
            return;
        }
        const pieces_set = client_side == WHITE ? white_pieces : black_pieces;
        // making a move
        if (selectedMoves.some(move => move[0] == i && move[1] == j)) {
            processMove(i, j);
        }
        // clicking on our piece
        else if (pieces_set.has(visual[i][j])) {
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

    // run when we click a promotion square
    function handlePromotion(piece) {
        // user cancelled
        if (piece == null) {
            setPromotionInfo(null);
            setMyTurn(true);
            setSelectedSquare(null);
            return;
        }
        const piece_number = piece_map[piece];
        const [[i, j], [rowDiff, colDiff]] = promotionInfo;
        const move = [[i, j], [rowDiff, colDiff], piece_number];
        executeMove(move);
    }

    // decide how to render board
    let visual_html = <></>;
    if (client_side == WHITE) {
        visual_html = visual.map((row, i) =>
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
        )
    } else {
        visual_html = visual.toReversed().map((row, i) =>
            row.toReversed().map((piece, j) => (
                <ChessSquare
                    key={`${i}-${j}`}
                    i={4 - i}
                    j={4 - j}
                    visual={visual}
                    handleClick={handleClick}
                    selectedSquare={selectedSquare}
                    selectedMoves={selectedMoves} />
            ))
        )
    }

    const promo_pieces = client_side == WHITE ? white_promo_pieces : black_promo_pieces;

    return (
        <div className='relative h-screen bg-gray-900 flex items-center justify-center text-white'>
            <div className={`absolute top-0 left-0 h-20 aspect-square`}>
                <img src={arrow_back} className={`h-full aspect-square
                hover:border-2 hover:border-red-500 hover:cursor-pointer rounded-full`}
                    alt={'x'} onClick={() => navigate('/')} />
            </div>
            {/* W/L info at top */}
            {(winStatus == 1 || winStatus == -1) &&
                <div className={`absolute top-0 h-1/8 text-3xl font-bold flex flex-col justify-center`}>
                    {winStatus == 1 && <h1 className='text-green-500'>You won!</h1>}
                    {winStatus == -1 && <h1 className='text-red-500'>You lost!</h1>}
                </div>}
            <div className="grid grid-cols-5 grid-rows-5 h-3/4 aspect-square border-2 border-gray-300">
                {visual_html}
            </div>
            {/* Arrow indicating who's turn */}
            <div className={`absolute left-0 mr-4 h-20 aspect-square`}>
                <img src={myTurn ? arrow_down : arrow_up} className={`h-full aspect-square`} />
            </div>
            {/* Promotion info at bottom */}
            {promotionInfo &&
                <div className={`absolute bottom-0 h-1/8
                flex flex-col text-center`}>
                    <h1 className='text-3xl font-bold'>
                        Promotion
                    </h1>
                    <div className={`flex flex-row justify-center h-full`}>
                        {promo_pieces.map(piece =>
                            <img src={image_map[piece]}
                                className={`h-full aspect-square hover:border-2 hover:border-fuchsia-500
                                    hover:cursor-pointer`}
                                alt={piece}
                                onClick={() => handlePromotion(piece)} />
                        )}
                        <img src={x}
                            className={`h-full aspect-square hover:border-2 hover:border-fuchsia-500
                                    hover:cursor-pointer`}
                            alt={'x'}
                            onClick={() => handlePromotion(null)} />
                    </div>
                </div>}
        </div>
    );
}

// a chess square
function ChessSquare({ i, j, visual, handleClick, selectedSquare, selectedMoves }) {
    const piece = visual[i][j];
    let color = (i + j) % 2 == 0 ? 'bg-amber-100' : 'bg-amber-800';
    let image = image_map[piece];
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

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
