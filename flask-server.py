from flask import Flask, render_template, request
from flask_socketio import SocketIO, disconnect, emit
import group_manager as gm

app = Flask(__name__)
manager = gm.GroupManager()
ip2ID = {}

@app.route("/")
def index():
    return render_template("client.html")
socketio = SocketIO(app)

@socketio.event
def connect():
    sid = request.sid
    ip = request.environ["REMOTE_ADDR"]
    port = request.environ["REMOTE_PORT"]
    socketio.emit("addr",{"ip": ip,"port":port}, room=sid)
    ip2ID[sid] = ip
    
@socketio.event
def join(data):
    sid = request.sid
    if manager.add_client(sid, data["name"], data["group"]):
        # user was successfully added to the group manager
        print(data["name"] + " has JOINED group: " + data["group"])
        socketio.emit("joinStatus","ok", room=sid)

        # notify every member of a group that a client has joined (including this client)
        for socket in manager.get_group_sockets(data["group"]):
                socketio.emit("addUser", data, to=socket)
                socketio.emit("updateUsers", {"users": manager.get_group_names(data["group"])})

    else:
        # username in this group has been taken
        print(sid + " has FAILED to join group: " + data["group"])
        socketio.emit("joinStatus","0", room=sid)
        
#
# recv - Transmits data from one client to other client(s) depending on the target
#
@socketio.event
def recv(data):
    sid = request.sid
    print("received '" + data["message"] + "' from " + data["name"] + " to " + data["target"] + " for group " + data["group"])
    if data["target"] == "all":
        for socket in manager.get_group_sockets(data["group"]):
            if socket != sid:
                socketio.emit("recvMsg", data, to=socket)
    else:
        socket = manager.get_group_socket_from_name(data["group"], data["target"])
        if socket != None:
            socketio.emit("recvMsg", data, to=socket)
            
#     
# send - Sends a message to all connected clients
#
@socketio.event
def send(data):
    socketio.emit("recvMsg", {"server": str(data)})

    
#
# disconnectUser - Disconnects a user from their group and notifies the group members of it
#
@socketio.event
def disconnectUser(data):
    sid = request.sid
    print("disconnecting " + data["name"] + " from group " + data["group"])

    # remove this client from the group
    manager.remove_client_from_group(data["group"], sid, data["name"])

    # tell all clients in this group that this client has disconnected    
    for socket in manager.get_group_sockets(data["group"]):
            socketio.emit("removeUser", data, to=socket)
            socketio.emit("updateUsers", {"users": manager.get_group_names(data["group"])})
            
@socketio.event
def disconnect():
    sid = request.sid
    print('disconnect ', sid)

if __name__ == '__main__':
    socketio.run(app)