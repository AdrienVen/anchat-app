class GroupManager:

    class Client:
        def __init__(self, socket, name):
            self.socket = socket
            self.name = name


    def __init__(self):
        self.groups = {}


    #
    # add_client - Attempts to add a client with a socket and name to a group, returns True only if the name is unused in that group
    #
    def  add_client(self, socket, name, group):
        if self.groups.get(group) == None:
            # create the group and add the client
            self.groups[group] = [self.Client(socket, name)]
        else:
            # determine if the name has already been used
            for client in self.groups[group]:
                if client.name == name:
                    return False 

            # add the client to the group
            self.groups[group].append(self.Client(socket, name))
            
        return True


    #
    # remove_client_from_group - Removes a client by their name and/or socket from a given group
    #
    def remove_client_from_group(self, group, socket = None, name = None):
        for client in self.groups.get(group, []):
            # remove the client from the group
            if client.name == name or client.socket == socket:
                self.groups[group].remove(client)

                # delete the group if there are no clients left inside
                if len(self.groups[group]) == 0:
                    del self.groups[group]


    #
    # remove_client - Removes a client from a group by their socket and/or name
    #
    def remove_client(self, socket = None, name = None):
        for group in self.groups.keys():
            # find the group the client belongs to
            for client in self.groups[group]:
                if client.name == name or client.socket == socket:
                    #remove the client from the group
                    self.groups[group].remove(client)

                    # delete the group if there are no clients left inside
                    if len(self.groups[group]) == 0:
                        del self.groups[group]


    #
    # get_group_names - Returns a list of all client names in a group
    #
    def get_group_names(self, group):
        names = []
        for client in self.groups.get(group, []):
            names.append(client.name)
        return names


    #
    # get_group_sockets - Returns a list of all client sockets in a group
    #
    def get_group_sockets(self, group):
        sockets = []
        for client in self.groups.get(group, []):
            sockets.append(client.socket)
        return sockets