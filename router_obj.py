import socket, sys, threading
import json
import signal
import time

SERVER_PORT = 9875
CLIENT_PORT = 9876

class ChatRouterObj(threading.Thread):
    def __init__(self, host='localhost'):
        threading.Thread.__init__(self)
        self.server_port = SERVER_PORT
        self.client_port = CLIENT_PORT
        self.host = host
        self.servers_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_connections = {}
        self.client_connections = {} # current connections
        self.users = []
        self.user_msgs = {}

        try:
            self.servers_socket.bind((self.host, self.server_port))
            self.clients_socket.bind((self.host, self.client_port))
        except socket.error:
            print('Bind failed %s' % (socket.error))
            sys.exit()

        self.servers_socket.listen(10)
        print("Listening for servers")
        self.clients_socket.listen(10)
        print("Listening for clients")

    def exit(self):
        self.servers_socket.close()
        self.clients_socket.close()

    def accept_servers(self):
        print('Waiting for connections from servers on port %s' % (self.server_port))
        # We need to run a loop and create a new thread for each connection
        while True:
            conn, addr = self.servers_socket.accept()
            self.server_connections[addr[1]] = conn
            print("got new server connection", addr[0], addr[1])
            threading.Thread(target=self.receive_server_msg, args=(conn, addr)).start()

    def receive_server_msg(self, conn, addr):
        while True:
            try:
                data = conn.recv(1024)
                msg = data.decode('utf-8')
            except Exception as e:
                print(str(e))
                # self.broadcast(username, username+"(%s, %s) is offline\n" % addr)
                conn.close() # Close
                del self.server_connections[addr[1]]
                print("removed server ", addr[1])
                return            

    def receive_client_msg(self, username, conn, addr):
        if username in self.user_msgs:
            for pending_msg in self.user_msgs[username]:
                print(username, " pending msg ", pending_msg)
                self.client_connections[username].send(bytes(pending_msg,'utf-8'))
                time.sleep(0.1)
            self.user_msgs[username] = []
        while True:
            try:
                data = conn.recv(1024)
                msg = data.decode('utf-8')
                #print(username + ": " + data.decode('utf-8'))
                if msg == 'list':
                    users = self.users
                    users_json = json.dumps(users)
                    self.client_connections[username].send(bytes("list:" + users_json,'utf-8'))
                else:
                    user_chat = data.decode('utf-8')
                    if "-" in user_chat:
                        user, chat_msg = user_chat.split("-")
                        send_msg = username + ": " + chat_msg
                        self.send_to_servers(username + " - " + user + " : " + chat_msg)
                        if user in self.client_connections:
                            self.client_connections[user].send(bytes(send_msg,'utf-8'))
                        else:
                            #print("User:", user, "is offline, saving to queue")
                            self.send_to_servers("User: " + user + " is offline, saving to queue")
                            time.sleep(0.1)
                            if user in self.user_msgs:
                                #print("Found user msg q, appending")
                                self.user_msgs[user].append(send_msg)
                                #print(user, " msgs ", self.user_msgs[user])
                                self.send_to_servers(user + " msgs " + str(self.user_msgs[user]))
                            else:
                                #print("Creating new user msg q")
                                self.user_msgs[user] = [send_msg]
                                #print(user, " msgs ", self.user_msgs[user])
                                self.send_to_servers(user + " msgs " + str(self.user_msgs[user]))

                    else:
                        print("ignoring msg", user_chat)

            except Exception as e:
                print(str(e))
                # self.broadcast(username, username+"(%s, %s) is offline\n" % addr)
                conn.close() # Close
                del self.client_connections[username]
                return
    
    def accept_clients(self):
        print('Waiting for connections from clients on port %s' % (self.client_port))
        # We need to run a loop and create a new thread for each connection
        while True:
            conn, addr = self.clients_socket.accept()
            print("got new client connection", addr[0], addr[1])
            data = conn.recv(1024)
            username = data.decode('utf-8')
            if (username not in self.client_connections):
                self.client_connections[username] = conn
                print(username, "connected")
                self.send_to_servers("user:" + username)
                #for server_conn in self.server_connections:
                #    server_conn.send(bytes("user:" + username, 'utf-8'))
                threading.Thread(target=self.receive_client_msg, args=(username, conn, addr)).start()
            
            userExists = False
            for user in self.users:
                if username == user:
                    userExists = True
            if userExists == False:
                self.users.append(username)

    def send_to_servers(self, msg):
        for addr, server_conn in self.server_connections.items():
            server_conn.send(bytes(msg, 'utf-8'))


if __name__ == '__main__':
    router = ChatRouterObj()
    threading.Thread(target=router.accept_servers, args=()).start()
    threading.Thread(target=router.accept_clients, args=()).start()
