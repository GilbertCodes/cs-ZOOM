from socket import *
from threading import Thread
import sys, select
import datetime
import time

users = []
'''
users = [
    { 
        username:
        password:
        ip_address:
    }
    {
        username:
        password:
        ip_address:
    }
]
'''
blocked_users = []
server_messages = []


# acquire server host and port from command line parameter
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT INVALID_INPUT======\n")
    exit(0)
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
invalid_input = int(sys.argv[2])
serverAddress = (serverHost, serverPort)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)




"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket, invalidInput):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        self.invalidInput = invalidInput
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
        
    def run(self):
        message = ''

        # self.process_login()
        
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            message = data.decode()
            
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.clientAlive = False
                print("===== the user disconnected - ", self.clientAddress)
                break
            messageSaved = message
            message = message.split(" ")
            # print("messageSaved")
            # print(messageSaved)
            # print("message[0]")
            # print(message[0])
            # print("message[1]")
            # print(message[1])
            print("message")
            print(message)
            
            # handle message from the client
            if message[0] == 'login':
                print("[recv] New login request")
                isLoggedIn = self.process_login(messageSaved)
                self.clientSocket.send(isLoggedIn.encode())

            elif message[0] == 'BCM':
                username = self.checkUser(clientAddress)
                print(f"{datetime.datetime.now()} " )
                message = 'download filename'
                print("[send] " + message)
                self.clientSocket.send(message.encode())
            elif message[0] == 'ATU':
                print("[recv] ATU request")
            else:
                print("[recv] " + message)
                print("[send] Cannot understand this message")
                message = 'Cannot understand this message'
                self.clientSocket.send(message.encode())
    
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    def process_login(self, message):
        # errorCounter = 0

        # self.clientSocket.send("request username".encode())
        # # self.clientSocket.send("success username".encode())   
        # username = self.clientSocket.recv(1024).decode()
        message = message.split(" ")
        username = message[1]
        password = message[2]

        print("username and password")
        print(username)
        print(password)

        for blocked in blocked_users:   
            if username == blocked['username']:
                if time.time() - blocked['time'] > 10:
                    del blocked
                else:
                    return "user has been blocked for 10 seconds"

        # check username
        if self.checkPassword(username) == password:
            # process password
            new_user = { "username": username, "password": password, 
            "ip_address": self.clientAddress }
            users.append(new_user)
            return "success"
        else:
            
            blocked_user = { "username": username, "time": time.time(), "attempts": 0
            }

            #check if blocked
            #check if attempts > invalid input
            
            checker = True
            for blocked in blocked_users:
                
                if blocked['username'] == username:
                    checker = False
                    if blocked['attempts'] >= invalid_input:
                        return "user has been blocked for 10 seconds"
                    else:
                        blocked['attempts'] += 1
                        blocked['time'] = time.time()
            
            if checker == True:
                blocked_users.append(blocked_user)
                
            return "Incorrect username or password."

    def checkUsername(self, username):
        f = open("credentials.txt", "r")
        userList = f.readlines()

        for users in userList:
            userInfo = users.split(" ")
            if userInfo[0] == username:
                return True

        return False

    def checkPassword(self, username):
        f = open("credentials.txt", "r")
        userList = f.readlines()

        for users in userList:
            userInfo = users.split(" ")
            if userInfo[0] == username:
                return userInfo[1].rstrip()

        return False

    def checkUser(self, ip_address):
        for address in users:
            if address['ip_address'] == ip_address:
                return address['username']
            

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt, invalid_input)
    clientThread.start()

