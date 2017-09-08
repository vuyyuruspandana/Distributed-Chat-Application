import socket, sys, threading
import select
import gnupg
import json

PORT = 9876

class ChatClientObj(threading.Thread):

    def __init__(self, port, host='localhost'):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, port))
        self.all_users = []
        self.chat_user = ""
        # Create public/private key if doesn't exist

    def send_message(self, msg):
        # Encrypt chat messages in this method
        data = bytes(msg, 'utf-8')
        self.socket.send(data)

    def ReceiveMessage(self):
        # Decrypt chat messages in this method
        while(True):
            data = self.socket.recv(1024)
            if data:
                msg = data.decode('utf-8')
                cmd, cmd_data = msg.split(":")
                if cmd == 'list':
                    self.all_users = json.loads(cmd_data)
                    print("Users:", self.all_users)
                    print("Select user to chat")
                    #self.chat_user = input("Select user to chat:")
                else:
                    print(msg)

    def ReceiveAllUsers(self):
        data = self.socket.recv(1024)
        msg = data.decode('utf-8')
        users = json.loads(msg)
        print("Users:", users)
        for user in users:
            print("User:", user)
        self.all_users = users
        self.chat_user = input("Select user to chat:")


    def run(self):
        print("Starting Client")

        # Currently only sends the username
        self.username = input("Username: ")
        data = bytes(self.username, 'utf-8')
        self.socket.send(data)

        # self.ReceiveAllUsers()

        # Need to get session passphrase

        # Starts thread to listen for data
        threading.Thread(target=self.ReceiveMessage).start()

        while(True):
            if self.chat_user == "":
                msg = input()
                for user in self.all_users:
                    if user == msg:
                        self.chat_user = user
                        break
            if self.chat_user != "":
                user_msg = input(self.chat_user + ": ")
                msg = self.chat_user + "-" + user_msg
            self.send_message(msg)
            #self.ReceiveMessage()

if __name__ == '__main__':
    client = ChatClientObj(PORT)
    client.start() # This start run()
