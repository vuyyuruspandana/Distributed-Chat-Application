import socket, sys, threading
import json
import signal
import time

SERVER_PORT = 9875

class ChatServerObj(threading.Thread):
    def __init__(self, port, host='localhost'):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, port))
        self.all_users = []
        self.chat_user = ""
        self.connections = {} # current connections
        self.users = []
        self.user_msgs = {}

    def run(self):
        print("Starting Server")
        while(True):
            data = self.socket.recv(1024)
            if data:
                msg = data.decode('utf-8')
                print(msg)
                if msg.count(':') == 1:
                    cmd, cmd_data = msg.split(":")
                    if cmd == 'user':
                        username = cmd_data
                        userExists = False
                        for user in self.users:
                            if username == user:
                                userExists = True
                        if userExists == False:
                            self.users.append(username)
                            print(self.users)
                #else:
                #    print("parse", msg)

    def AddClientConn(self, conn, addr):
        print("Added client connection", addr[0], addr[1])

if __name__ == '__main__':
    server = ChatServerObj(SERVER_PORT)
    server.start() # This start run()
    