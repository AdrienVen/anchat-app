# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 17:59:00 2021

@author: adven
"""
import eventlet
import socketio
import socket as sck
import group_manager as gm

sio = socketio.Server()
manager = gm.GroupManager()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'client.html'}
})
#
# connect - Registers when a client has connected
#
ip2ID = {}
@sio.event
def connect(sid, environ):
    print('connect ',environ["REMOTE_ADDR"],"on port",environ["REMOTE_PORT"])
    sio.emit("addr",{"ip": environ["REMOTE_ADDR"],"port":environ["REMOTE_PORT"]}, room=sid)
    ip2ID[sid] = environ["REMOTE_ADDR"]
    

#
# join - Attempts to add a client into a group and sends back a join status message
#
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

#Sends a message to all connected clients
@sio.event
def send(data):
    sio.emit("recvMsg", {"server": str(data)})
    
#
# recv - Transmits data from one client to other client(s) depending on the target
# 
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


#
# disconnectUser - Disconnects a user from their group and notifies the group members of it
#
@sio.event
def disconnectUser(sid, data):
    print("disconnecting " + data["name"] + " from group " + data["group"])

    # remove this client from the group
    manager.remove_client_from_group(data["group"], sid, data["name"])

    # tell all clients in this group that this client has disconnected    
    for socket in manager.get_group_sockets(data["group"]):
            sio.emit("removeUser", data, to=socket)
            sio.emit("updateUsers", {"users": manager.get_group_names(data["group"])})

    


#     
# send - Sends a message to all connected clients
#
@sio.event
def exchange_addresses(sid, data):
    print(data["user"],"has submitted a game request with",data["to"])
    ip_A = ip2ID[sid]
    sendPort_A = data["sendPort"]
    listenPort_A = data["listenPort"]
    
    
    ip_B = ip2ID[manager.user_name_to_socket[data["to"]]]
    sendPort_B = data["listenPort"]
    listenPort_B = data["sendPort"]
    
    socket_a = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
    print("sending "+ip_B+','+sendPort_A+','+listenPort_A,"to A")
    socket_a.sendto((ip_B+','+sendPort_A+','+listenPort_A+','+"GAME").encode(), (ip_A, 12005))
    
    socket_b = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
    print("sending "+ip_A+','+sendPort_B+','+listenPort_B,"to B")
    socket_b.sendto((ip_A+','+sendPort_B+','+listenPort_B+','+"ENEMY_TURN").encode(), (ip_B, 12005))
    
#
# disconnect - Prints that a socket has disconnected 
#(is this automatic? if so the sid should be removed from the manager and a message sent to everyone in that group)
#
@sio.event
def disconnect(sid):
    print('disconnect ', sid)


    
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 65432)), app)