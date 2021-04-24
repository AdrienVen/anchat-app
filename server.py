# -*- coding: utf-8 -*-
# server.py - made by Adrien Ventugol and Alex Gonsalves

import eventlet
import socketio
import socket as sck
import group_manager as gm

sio = socketio.Server(async_mode="eventlet")
manager = gm.GroupManager()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})
ip2ID = {}

@sio.event
def connect(sid, environ):
    print('connect ',environ["REMOTE_ADDR"],"on port",environ["REMOTE_PORT"])
    sio.emit("addr",{"ip": environ["REMOTE_ADDR"],"port":environ["REMOTE_PORT"]}, room=sid)
    ip2ID[sid] = environ["REMOTE_ADDR"]
    

@sio.event
def join(sid,data):
    if manager.add_client(sid, data["name"], data["group"]):
        # user was successfully added to the group manager
        print(data["name"] + " has JOINED group: " + data["group"])
        sio.emit("joinStatus","ok", room=sid)

        # notify every member of a group that a client has joined (including this client)
        for socket in manager.get_group_sockets(data["group"]):
                sio.emit("addUser", data, to=socket)
                sio.emit("updateUsers", {"users": manager.get_group_names(data["group"])})

    else:
        # username in this group has been taken
        print(sid + " has FAILED to join group: " + data["group"])
        sio.emit("joinStatus","0", room=sid)


@sio.event
def recv(sid, data):
    print("received '" + data["message"] + "' from " + data["name"] + " to " + data["target"] + " for group " + data["group"])
    if data["target"] == "all":
        for socket in manager.get_group_sockets(data["group"]):
            if socket != sid:
                sio.emit("recvMsg", data, to=socket)
    else:
        socket = manager.get_group_socket_from_name(data["group"], data["target"])
        if socket != None:
            sio.emit("recvMsg", data, to=socket)


@sio.event
def disconnectUser(sid, data):
    print("disconnecting " + data["name"] + " from group " + data["group"])

    # remove this client from the group
    manager.remove_client_from_group(data["group"], sid, data["name"])

    # tell all clients in this group that this client has disconnected    
    for socket in manager.get_group_sockets(data["group"]):
            sio.emit("removeUser", data, to=socket)
            sio.emit("updateUsers", {"users": manager.get_group_names(data["group"])})


@sio.event
def exchange_addresses(sid, data):
    # get client A information
    print(data["name"],"has submitted a game request with",data["to"])
    ip_A = ip2ID[sid]
    sendPort_A = data["sendPort"]
    listenPort_A = data["listenPort"]

    # get client B information
    other_sid = manager.get_group_socket_from_name(data["group"], data["to"])
    print(other_sid)
    ip_B = ip2ID[other_sid]
    sendPort_B = data["listenPort"]
    listenPort_B = data["sendPort"]
    
    # send client B information to client A
    socket_a = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
    print("sending "+ip_B+','+sendPort_A+','+listenPort_A,"to A")
    socket_a.sendto((ip_B+','+sendPort_A+','+listenPort_A+','+"GAME").encode(), (ip_A, 12005))
    
    # send client A information to client B
    socket_b = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
    print("sending "+ip_A+','+sendPort_B+','+listenPort_B,"to B")
    socket_b.sendto((ip_A+','+sendPort_B+','+listenPort_B+','+"ENEMY_TURN").encode(), (ip_B, 12005))


@sio.event
def send(data):
    sio.emit("recvMsg", {"server": str(data)})


@sio.event
def disconnect(sid):
    print('disconnect ', sid)

def main(arg1, arg2):
    print(arg1,arg2)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)