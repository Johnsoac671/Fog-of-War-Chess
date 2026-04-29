'''
Server for our 1v1ing the bot backend using Flask
'''

from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import uuid
import random
# import agents
from engine.agents.agent import Agent
from engine.agents.random_agents import RandomAgent, EagerRandomAgent
from engine.agents.monte_carlo_agent import MonteCarloAgent
from engine.agents.alpha_beta_agent import AlphaBetaAgent
# import dark chess game
from engine.game.dark_chess import Game

# try to import game engine
# try:
#     from engine.game.dark_chess import Game
#     ENGINE_LOADED = True
# except ImportError as e:
#     print(f"Engine import failed: {e}")
#     ENGINE_LOADED = False

app = Flask(__name__)
# allows react client to connect
CORS(app)

class ClientGameState:
    def __init__(self, game: Game, client_side: int, agent: Agent):
        self.game = game
        self.client_side = client_side
        self.agent = agent
        
    # get visualization for the client
    def get_frontend_visualization(self):
        return self.game.get_frontend_visualization()
    
    # only call if it is client's turn
    def get_legal_moves(self):
        return self.game.get_legal_moves()
    
    # agent makes a move
    def make_agent_move(self):
        move = self.agent.choose_move(self.game)
        self.game.take_action(move)
    
    # client makes a move, make sure they can actually do this
    def make_client_move(self, move):
        self.game.take_action(move)

active_games = {}

@app.route('/test')
def test():
    ret = {}
    ret['message'] = 'success'
    return jsonify(ret)

# starts a new game
@app.route('/start', methods=['POST'])
def startGame():
    data = request.get_json()
    # which side is the client on
    side = data['side']
    if side == 'Random':
        side = random.choice(['White', 'Black'])
    agent = data['agent']
    # determine color of agent (expects 'W' or 'B')
    agent_color = 'B' if side == 'White' else 'W'
    agent_object = None
    # possible agent strings = ['Random', 'EagerRandom', 'AlphaBeta', 'MonteCarlo']
    if agent == 'Random':
        agent_object = RandomAgent(name=agent, color=agent_color)
    elif agent == 'EagerRandom':
        agent_object = EagerRandomAgent(name=agent, color=agent_color)
    elif agent == 'AlphaBeta':
        agent_object = AlphaBetaAgent(name=agent, color=agent_color)
    elif agent == 'MonteCarlo':
        agent_object = MonteCarloAgent(name=agent, color=agent_color)
    new_game_id = uuid.uuid4()
    client_side = 0 if side == 'Black' else 1
    # create new dark chess game
    new_game = Game(client_side=client_side)
    new_client_game = ClientGameState(new_game, client_side, agent_object)
    active_games[new_game_id] = new_client_game
    # client must know visual board and legal moves
    visual = new_client_game.get_frontend_visualization()
    legal_moves = new_client_game.get_legal_moves()
    return jsonify({
        'game_id': new_game_id,
        'visual': visual,
        'legal_moves': legal_moves,
        'client_side': client_side
    })
    
if __name__ == "__main__":
    app.run(debug=True)
