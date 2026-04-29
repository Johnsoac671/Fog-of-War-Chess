import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Main from './Main.jsx';
import Game from './Game.jsx';

export const url = 'http://127.0.0.1:5000';

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Main />} />
                <Route path="/game" element={<Game />} />
            </Routes>
        </BrowserRouter>
    );
}
