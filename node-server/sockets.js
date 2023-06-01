const { gameStart, possibleMoves } = require("./gamePlay")

let roomPlayers = []
let privateRooms = {}
let room = 1

function listen(io) {
  function joinPublicRoom(socket, playerData) {
    socket.join(room)
    // console.log(io.sockets.adapter.rooms)
    playerData.socket = socket.id
    if (!roomPlayers.find((p) => p.socket === playerData.socket)) {
      roomPlayers.push(playerData)
    }
    console.log({ playerData, players: roomPlayers.length })

    io.in(room).emit("player_joined", { roomPlayers, room })
    if (roomPlayers.length === 5) {
      room += 1
      roomPlayers.splice(0)
    }
  }

  function joinPrivateRoom(socket, playerData) {
    const privateRoom = playerData.room

    socket.to(privateRoom).emit("isStarted")
    privateRooms[privateRoom] = privateRooms[privateRoom] || []
    if (privateRooms[privateRoom].length === 5) {
      socket.emit("roomFull")
      return
    }
    socket.join(privateRoom)

    if (!privateRooms[privateRoom].find((p) => p.pid === playerData.pid)) {
      privateRooms[privateRoom].push(playerData)
    }

    playerData.socket = socket.id
    io.in(privateRoom).emit("playerJoined", {
      roomPlayers: privateRooms[privateRoom],
      room: privateRoom,
    })
  
  }


  io.on("connection", (socket) => {
    console.log("User connected", socket.id)
    socket.on("ready", (playerData) => {
      playerData = playerData ?? {}
      if (playerData.room) {
        joinPrivateRoom(socket, playerData)
        console.log("private: ", privateRooms[playerData.room])
      } else {
        console.log("public")
        joinPublicRoom(socket, playerData)
      }
    })

    socket.on("started", ({ room, started }) => {
      console.log("started", started)
      if (started) {
        const startData = gameStart(roomPlayers.length)

        startData.possibleMoves = startData.hands.map(h=> possibleMoves(h, startData.startCard))
        io.to(room).emit("gameStarted", startData)
      }
    })
    socket.on("deal", (startGameData) => {
      console.log("Game on Guys!!!", startGameData)
      const currentRoom = startGameData.room || room
      io.in(currentRoom).emit("startGame", {
        ...startGameData,
        room: currentRoom,
      })
      if (typeof currentRoom === "number") {
        if (currentRoom === room) room += 1
        roomPlayers.splice(0)
      } else {
        delete privateRooms[currentRoom]
      }
    })

    socket.on("message", (message) => {
      console.log(message)
      io.in(message.room).emit("newMessage", message)
    })
    socket.on("emoji", (emoji) => {
      emoji
      console.log(emoji)
      io.in(emoji.room).emit("newEmoji", emoji)
    })

    socket.on("play", (playData) => {
      console.log(playData)
      socket.to(playData.room).emit("played", playData)
    })

    socket.on("playComplete", ({ turn, room, actions }) => {
      console.log({ turn, room, actions })
      io.in(room).emit("newTurn", { turn, actions })
    })

    socket.on("win", ({ winner, room }) => {
      console.log({ winner, room })
      io.in(room).emit("winner", { winner })
    })

    socket.on("disconnecting", (a) => {
      socket.rooms.forEach((currentRoom) => {
        io.to(currentRoom).emit("userDisconnect", { socket: socket.id })
        if (room === currentRoom) {
          roomPlayers = roomPlayers.filter((p) => p.socket !== socket.id)
        }

        if (privateRooms[currentRoom]) {
          privateRooms[currentRoom] = privateRooms[currentRoom].filter(
            (p) => p.socket !== socket.id
          )
        }
        console.log({ currentRoom, p: privateRooms[currentRoom] })
      })
      console.log(`Disconnecting: ${socket.id} ${a}`)
    })

    socket.on("disconnect", (reason) => {
      console.log(`User disconnected: ${reason}`)
    })
  })
}

module.exports = { listen }
