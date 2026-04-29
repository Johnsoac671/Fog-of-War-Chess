import { useState, useEffect } from 'react';
import { url } from './App.jsx';
import { useNavigate } from 'react-router-dom';

const sides = ['White', 'Random', 'Black'];
const agents = ['Random', 'EagerRandom', 'AlphaBeta', 'MonteCarlo'];

export default function Main() {
    const navigate = useNavigate();
    // selected slide
    const [side, setSide] = useState('Random');
    // selected agent
    const [agent, setAgent] = useState('Random');
    // runs when start button is clicked
    async function handleStart() {
        try {
            const response = await fetch(`${url}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    side, agent
                }),
            });
            if (!response.ok) {
                throw new Error();
            }
            const resJSON = await response.json();
            console.log("Game started:", resJSON);
            const { game_id, visual, legal_moves, client_side } = resJSON;
            // store the id for possible restore in future
            localStorage.setItem('chess_game_id', game_id);
            const state = { game_id, visual, legal_moves, client_side };
            // move to the game board
            navigate('/game', { state });
        } catch (err) {
            console.error("Error:", err);
            alert('error');
        }
    }
    return (
        <div className='h-screen bg-black flex items-center justify-center text-white'>
            <div className={`h-3/4 aspect-square bg-gray-950 flex flex-col overflow-y-auto
                justify-evenly items-center rounded-2xl border-2 p-10 text-center`}>
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
                {/* Start button */}
                <div className={`flex justify-center items-center w-1/4 p-4 rounded-3xl
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

// button for choosing which agent
function AgentButton({ agent_name, agent, setAgent }) {
    return (
        <div className={`flex flex-col justify-center items-center w-full h-10
            hover:bg-white/25 hover:cursor-pointer
            ${agent == agent_name ? 'bg-white/35' : ''}`}
            onClick={() => setAgent(agent_name)}>
            <h1 className='text-2xl font-bold'>
                {agent_name}
            </h1>
        </div>
    );
}
