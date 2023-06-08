import socketio
import numpy as np
import torch

sio = socketio.Client()


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
        
        turn = 0
        my_index = list(map(get_sid, room_players)).index(sio.sid)
        my_hand = payload['hands'][my_index]

        my_hand = hot_encode(my_hand)
        top_card = payload['startCard']
        top_card = hot_encode([top_card])
        wastes = top_card.clone()

        deck = torch.zeros(54)
        deck[0] = 40/54

        actions = torch.zeros([54])

        env_space = torch.stack([deck, my_hand, top_card, wastes], dim=0)

        print(env_space)
        print("shape: {}".format(env_space.size()))

        # if my_index == turn:
        #     @sio.emit("whereto", {'hand': my_hand, 'topCard': top_card})



sio.connect('http://localhost:4000')
sio.wait()   
