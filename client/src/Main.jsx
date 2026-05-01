import { useState, useEffect } from 'react';
import { url } from './App.jsx';
import { useNavigate } from 'react-router-dom';

const sides = ['White', 'Random', 'Black'];
const agents = ['Random', 'SmartRandom', 'AlphaBeta', 'MonteCarlo', 'MonteCarloTreeSearch', 'NeuralMCTS'];
const determinizers = ['IgnoranceIsBlissDeterminizer', 'BadDeterminizer', 'RandomDeterminizer', 'CheatingDeterminizer'];
const times = ['0.5s', '1s', '3s', '5s'];
import info from './assets/info.svg';

const description_map = {
    'Random': 'Randomly chooses a move from the legal moves',
    'SmartRandom': 'Always takes a move that wins if available, otherwise chooses a move at random from the pool of legal moves',
    'AlphaBeta': 'Uses alpha-beta pruning to choose the best move',
    'MonteCarlo': 'Plays 100 random games with each move, and chooses the one that wins the most',
    'MonteCarloTreeSearch': 'Uses a tree search to focus on moves that seem more promising',
    'NeuralMCTS': 'Monte Carlo Tree Search, but it uses a Neural Network to rate how good various starting moves are, to determine which branches to explore more',
    'IgnoranceIsBlissDeterminizer': 'Just assumes all unseen spaces are empty',
    'BadDeterminizer': 'Just assumes all unseen spaces are empty (except for the opposing king, who is assumed to be on a random unseen space if not visible)',
    'CheatingDeterminizer': 'Reveals all squares, basically makes the game regular chess',
    'RandomDeterminizer': 'Randomly places the opponent\'s hidden pieces onto space that are not currently visible to the active player',
}

export default function Main() {
    const navigate = useNavigate();
    // selected slide
    const [side, setSide] = useState('Random');
    // selected agent
    const [agent, setAgent] = useState('Random');
    // selected determinizer
    const [determinizer, setDeterminizer] = useState('IgnoranceIsBlissDeterminizer');
    // selected time between moves
    const [time, setTime] = useState('0.5s');
    // runs when start button is clicked
    async function handleStart() {
        try {
            const response = await fetch(`${url}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    side, agent, determinizer
                }),
            });
            if (!response.ok) {
                throw new Error();
            }
            const resJSON = await response.json();
            console.log("Game started:", resJSON);
            const { chess_game_id, visual, legal_moves, client_side } = resJSON;
            // store the id for possible restore in future
            localStorage.setItem('chess_game_id', chess_game_id);
            const state = { chess_game_id, visual, legal_moves, client_side, time };
            // move to the game board - sends state stuff over
            navigate('/game', { state });
        } catch (err) {
            console.error("Error:", err);
            alert('error');
        }
    }
    return (
        <div className='h-screen bg-black flex items-center justify-center text-white'>
            <div className={`h-full aspect-square bg-gray-950 flex flex-col overflow-y-auto
                justify-evenly items-center rounded-2xl border-2 p-8 text-center`}>
                <div className='text-5xl font-bold'>
                    Welcome to 5x5 Fog of War Chess!
                </div>
                {/* Choose a side */}
                <div className={`flex flex-col w-1/2 border-2 mt-5`}>
                    <h1 className='text-4xl font-bold p-4'>Choose a side</h1>
                    <div className='flex flex-row h-20 w-full'>
                        {sides.map(side_name => (
                            <SideButton side_name={side_name}
                                side={side}
                                setSide={setSide} />
                        ))}
                    </div>
                </div>
                {/* Choose an agent */}
                <div className={`flex flex-col w-1/2 border-2 mt-5 overflow-y-auto min-h-50`}>
                    <h1 className='text-4xl font-bold p-4'>Choose an agent</h1>
                    {/* List of agents */}
                    {agents.map(agent_name => (
                        <AgentButton agent_name={agent_name}
                            agent={agent}
                            setAgent={setAgent} />
                    ))}
                </div>
                {/* Choose a determinizer */}
                <div className={`relative flex flex-col w-1/2 border-2 mt-5 overflow-y-auto min-h-50`}>
                    <img src={info} className='absolute right-0 h-8 mt-1  mr-1 aspect-square hover:cursor-pointer'
                        onClick={() => alert('A determinizer is how the agent reasons about foggy squares')} />
                    <h1 className='text-4xl font-bold p-4'>Choose a determinizer</h1>
                    {/* List of determinizers */}
                    {determinizers.map(det => (
                        <AgentButton agent_name={det}
                            agent={determinizer}
                            setAgent={setDeterminizer} />
                    ))}
                </div>
                {/* Choose time between bot moves */}
                <div className={`flex flex-col w-1/2 border-2 mt-5`}>
                    <h1 className='text-4xl font-bold p-4'>Time between bot moves</h1>
                    <div className='flex flex-row h-20 w-full'>
                        {times.map(t => (
                            <SideButton side_name={t}
                                side={time}
                                setSide={setTime} />
                        ))}
                    </div>
                </div>
                {/* Start button */}
                <div className={`flex justify-center items-center w-1/4 p-4 mt-4 rounded-3xl
                    bg-green-700 hover:cursor-pointer hover:bg-green-700/50 border-2`}
                    onClick={handleStart}>
                    <h1 className='text-3xl font-bold'>
                        Start
                    </h1>
                </div>
            </div>
        </div>
    );
}

// button for choosing which side (white, black or random)
function SideButton({ side_name, side, setSide }) {
    return (
        <div className={`flex flex-col justify-center items-center w-full h-full
            hover:bg-white/25 hover:cursor-pointer
            ${side == side_name ? 'bg-white/35' : ''}`}
            onClick={() => setSide(side_name)}>
            <h1 className='text-2xl font-bold'>
                {side_name}
            </h1>
        </div>
    );
}

// button for choosing which agent OR determinizer
function AgentButton({ agent_name, agent, setAgent }) {
    return (
        <div className={`relative flex flex-col justify-center items-center w-full h-10
            hover:bg-white/25 hover:cursor-pointer z-0
            ${agent == agent_name ? 'bg-white/35' : ''}`}
            onClick={() => setAgent(agent_name)}>
            <h1 className='text-2xl font-bold'>
                {agent_name}
            </h1>
            <img src={info} className='absolute right-0 h-full aspect-square z-10'
                onClick={((e) => {
                    e.stopPropagation();
                    alert(description_map[agent_name]);
                })} />
        </div>
    );
}
