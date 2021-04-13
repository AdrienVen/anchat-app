class GroupManager:
    def __init__(self):
        self.groups = {}
        self.user_name_to_socket = {}
        self.user_socket_to_name = {}


    #
    # add_user_socket - Adds a new user socket to the socket to name dictionary
    #
    def add_user_socket(self, socket, name = None):
        self.user_socket_to_name[socket] = name


    #
    # remove_user_by_name - Removes a user by a non-None name from the socket to name and name to socket dictionaries
    #
    def remove_user_by_name(self, name):
        if name != None & self.is_name_member(name):
            socket = self.name_to_socket.pop(name)
            if self.is_socket_member(socket):
                del self.user_socket_to_name[socket]


    #
    # remove_user_by_socket - Removes a user by a socket from the socket to name and name to socket dictionaries
    #
    def remove_user_by_socket(self, socket):
        if self.is_socket_member(socket):
            name = self.user_socket_to_name.pop(socket)
            if name != None & self.is_name_member(name):
                del self.user_name_to_socket[name]


    #
    # is_name_member - Returns True if the given name belongs to a user
    #
    def is_name_member(self, name):
        return (self.user_name_to_socket.get(name,"N/A") != "N/A")


    #
    # is_socket_member - Returns True if the socket belongs to a user
    #
    def is_socket_member(self, socket):
        return socket in self.user_socket_to_name


    #
    # get_user_socket - Returns the socket that belongs to the given user name
    #
    def get_user_socket(self, name):
        return self.user_name_to_socket.get(name)


    #
    # get_user_name - Returns the user name that belongs to the given socket
    #
    def get_user_name(self, socket):
        return self.user_socket_to_name.get(socket)


    #
    # set_user_name - Sets the new user name to the value and key of the socket to name and name to socket dictionaries respectivley
    #
    def set_user_name(self, socket, name):
        if socket in self.user_socket_to_name:
            self.user_socket_to_name[socket] = name
        
        for old_name in self.user_name_to_socket.keys():
            if self.user_name_to_socket[old_name] == socket:
                del self.user_name_to_socket[old_name]
        
        self.user_name_to_socket[name] = socket


    #
    # is_name_available - Returns True if the name is not used by another user
    #
    def is_name_available(self, name):
        return not name in self.user_name_to_socket


    #
    # does_group_exist - Returns True if the group exists
    #
    def does_group_exist(self, group):
        return self.groups.get(group,"N/A") != "N/A"


    #
    # socket_join_group - Either adds a user's socket to an existing group or creates a new group
    #
    def socket_join_group(self, group, socket):
        if self.does_group_exist(group):
            if socket not in self.groups[group]:
                self.groups[group].append(socket)
        else:
            self.groups[group] = [socket]


    #
    # name_join_group - Gets a socket by the given user name and calls the socket_join_group function
    #
    def name_join_group(self, group, name):
        socket = self.user_name_to_socket[name]
        if socket != None:
            self.socket_join_group(group, socket)


    #
    # socket_in_group - Returns True if the group does exist and if that socket is in that group
    #
    def socket_in_group(self, group, socket):
        return self.does_group_exist(group) & (socket in self.groups[group])


    #
    # name_in_group - Returns True if the group does exist and if the socket belonging to that user name is in that group
    #
    def name_in_group(self, group, name):
        return self.socket_in_group(group, self.user_name_to_socket[name])


    #
    # socket_leave_group - Removes a socket from a group and deletes the group if there are no members left
    #
    def socket_leave_group(self, group, socket):
        if self.does_group_exist(group):
            self.groups[group].remove(socket)
            self.reset_socket_name(socket)
            if len(self.groups[group]) == 0:
                del self.groups[group]

    
    #
    # reset_socket_name - Removes a given socket user name
    #
    def reset_socket_name(self, socket):
        del self.user_name_to_socket[self.get_user_name(socket)]
        self.user_socket_to_name[socket] = None


    #
    # name_leave_group - Removes a socket belonging to that user name with the socket_leave_group function
    #
    def name_leave_group(self, group, name):
        socket = self.user_name_to_socket[name]
        if socket != None:
            self.socket_leave_group(group, socket)


    #
    # disconnect_by_socket - Disconnects a user from their group by socket and removes them from the user dictionaries
    #
    def disconnect_by_socket(self, socket):
        for group in self.groups.keys():
            if self.socket_in_group(group, socket):
                self.groups[group].remove(socket)

        self.remove_user_by_socket


    #
    # disconnect_by_name - Disconnects a user from their group by socket/name and removes them from the user dictionaries
    #
    def disconnect_by_name(self, name):
        socket = self.user_name_to_socket[name]
        if socket != None:
            for group in self.groups.keys():
                if self.socket_in_group(group, socket):
                    self.groups[group].remove(socket)

        self.remove_user_by_name(name)


    #
    # get_group_by_socket - Returns a group name that contains the given socket
    #
    def get_group_by_socket(self, socket):
        for group in self.groups.keys():
            if socket in self.groups[group]:
                return group

    
    #
    # get_group_members_by_socket - Returns a list of group members that are in the same group as the given socket
    #
    def get_group_members_by_socket(self, socket):
        return self.groups[self.get_group_by_socket(socket)]