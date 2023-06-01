import socketio

sio = socketio.Client()


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
        top_card = payload['startCard']

        # if my_index == turn:
        #     @sio.emit("whereto", {'hand': my_hand, 'topCard': top_card})



sio.connect('http://localhost:4000')
sio.wait()   
