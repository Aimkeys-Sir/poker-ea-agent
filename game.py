import socketio
import numpy as np
import torch
import random
from DQN import DQNAgent


sio = socketio.Client()

params  = dict()

params["first_layer_size"] = 256
params["second_layer_size"] = 128
params["third_layer_size"] = 64
params["weights_path"] = "weights/weights.h5"
params["learning_rate"] = 0.6
params["memory_size"] = 2500
params["load_weights"] = False
params['train'] = True
params["epsilon_decay_linear"] =0.9

count_games = 0

agent = DQNAgent(params)

def hot_encode(cards, length=54):
    tensor = torch.zeros(length)
    print(cards)
    tensor[cards] = 1.0
    return tensor

@sio.event
def connect():
    print("Connected")
    sio.emit("ready", {'pid': sio.sid})

@sio.event
def connect_error(error):
    print("an error occurred: ", error)

@sio.event
def disconnect():
    print("socket disconnected")

@sio.on('player_joined')
def player_joined(payload):
    print(payload)
    room = payload['room']
    room_players = payload['roomPlayers']

    if len(payload['roomPlayers'])>1 and sio.sid == payload['roomPlayers'][0]['pid'] :
        sio.emit("started", {'started': True, 'room': room})

    @sio.on('gameStarted')
    def on_start(payload):
        print(payload)

        def get_sid(p):
            return p["pid"]
        
        my_index = list(map(get_sid, room_players)).index(sio.sid)
        turn = 1 if my_index == 0 else 0
        my_hand = payload['hands'][my_index]
        top_card = payload['startCard']
        poss_moves = payload['possibleMoves'][my_index]

        # env_space =agent.get_env_space(agent_hand=my_hand,top_card=top_card,wastes=[top_card],deck_size=40,actions=[],player_turn=turn, poss_moves=poss_moves)

        simple_env = agent.simple_env(agent_hand=my_hand, top_card=top_card,)

        # action_space = agent.get_action_space(poss_moves=poss_moves)
        print("\nenv space")
        
        # print(simple_env.size())
        print(simple_env)


def play(state):
   if not params["train"]:
       epsilon = 0.01
   else:
       epsilon =  1 - (count_games * params['epsilon_decay_linear'])
   if random.uniform(0,1)<epsilon:
       #choose random move
       move = []
   else:
       prediction = agent(state)

sio.connect('http://localhost:4000')
sio.wait()   
