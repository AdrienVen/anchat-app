# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 17:59:00 2021

@author: adven
"""
import eventlet
import socketio
import group_manager as gm

sio = socketio.Server()
manager = gm.GroupManager()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'login.html'}
})



@sio.event
def connect(sid, environ):
    print('connect ', sid)
    
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
    for socket in manager.groups[data["group"]]:
        if socket != sid:
            sio.emit("recv", data, to=socket)
            
#Sends a message to all connected clients
@sio.event
def send(data):
    sio.emit("recv", {"server": str(data)})

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 65432)), app)