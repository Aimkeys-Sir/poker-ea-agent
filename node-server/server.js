const http = require('http')
const io = require('socket.io')

const sockets = require('./sockets')

const httpServer = http.createServer()
const socketServer = io(httpServer,{
    cors:{
        origin: "*",
        methods: ["GET", "POST"]
    }
})

httpServer.listen(4000, ()=>{
    console.log('server is running at 4000')
})


sockets.listen(socketServer)
