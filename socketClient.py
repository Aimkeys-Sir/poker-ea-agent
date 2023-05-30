from socketIO_client import SocketIO, LoggingNamespace

def on_connect():
    print("connected")

def on_disconnect():
    print("disconnected")

def on_ready():
    print("I'm ready")

def on_error(*args):
    print(f"Error occured: {args}")

socketIO = SocketIO("localhost", 4000, LoggingNamespace)

socketIO.on('connect', on_connect)
socketIO.on('error', on_error)
socketIO.emit("ready", on_ready)