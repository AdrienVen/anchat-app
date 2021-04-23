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


ip2ID = {}
@sio.event
def connect(sid, environ):
    print('connect ',environ["REMOTE_ADDR"],"on port",environ["REMOTE_PORT"])
    sio.emit("addr",{"ip": environ["REMOTE_ADDR"],"port":environ["REMOTE_PORT"]}, room=sid)
    ip2ID[sid] = environ["REMOTE_ADDR"]
    
#adds a client sid to a groupchat data["group"]
@sio.event
def join(sid,data):
    print(sid,"wants to join/create group:",data["group"])
    
    if manager.is_name_member(data["username"]):
            # name already taken
            sio.emit("joinStatus","0", room=sid)
    else:
        # name not taken
        manager.set_user_name(sid, data["username"])
        manager.socket_join_group(data["group"], sid)
        sio.emit("joinStatus","ok", room=sid)


#transmits data from one sender(sid) to the rest of the group(data["group"]).
@sio.event
def recv(sid, data):
    print("received ", data["message"] + "from " + data["user"] + " for " + data["group"])
    for client_id in manager.groups[data["group"]]:
        if client_id != sid:
            sio.emit("recv", data, to=client_id)

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
    
    
    
@sio.event
def send_addr(sid, data):
    print("send address"+data["ip"]+data["listenPort"]+" to "+data["to"])
    game_sock = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
    game_sock.sendto(data["ip"]+','+data["sendPort"]+','+data["listenPort"], (data["ip"], 12005))
    socket = manager.user_name_to_socket[data["to"]]
    temp = data["sendPort"]
    data["sendPort"] = data["listenPort"]
    data["listenPort"] = data["sendPort"]
    sio.emit("recv_addr", data, to=socket)
    
@sio.event   
def return_addr(sid,data):
        print("send address"+data["ip"]+data["port"]+" to "+data["to"])
        socket = manager.user_name_to_socket[data["to"]]
        sio.emit("return_addr", data, to=socket)

#Sends a message to all connected clients
@sio.event
def send(data):
    sio.emit("recv", {"server": str(data)})

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 65432)), app)