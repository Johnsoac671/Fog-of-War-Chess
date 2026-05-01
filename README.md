# Dark Chess Agents

Starter repository for comparing AI agents in a Dark Chess / Fog-of-War MiniChess environment.

## Current Features

- 5x5 mini chess board
- Basic game state representation
- Simplified movement rules
- Fog-of-war style visibility function
- Random agent
- Minimax agent
- MCTS draft agent
- Evaluation script for head-to-head matches

## Minichess Implementation
https://github.com/patrik-ha/explainable-minichess or [https://arxiv.org/abs/2211.05500](https://arxiv.org/abs/2211.05500)
## Notes

This is an early draft meant to provide a starting codebase for the team project.
The rules are intentionally simplified and can be refined later.

## Run

```bash
pip install -r requirements.txt
python main.py
python evaluate.py
```
## Running Website Locally
[Hosted link](https://fog-of-war-chess.azurewebsites.net/)

1. Clone repository
2. Create a Python venv (optional)
- python3 -m venv .venv
3. Activate venv (optional)
- source .venv/bin/activate
4. Install requirements in root
- pip install -r requirements.txt
5. Run the app
- python3 app.py
6. Setup frontend
- cd client
7. Install dependencies
- npm install
8. start dev server
- npm run dev

Then the website should be available at [http://localhost:5173](http://localhost:5173)
