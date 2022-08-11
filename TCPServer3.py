from socket import *
from threading import Thread
import sys, select
import datetime
import time
import pickle

users = []
'''
users = [
    { 
        u_id:
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
rooms = []
num_messages = 1
num_users = 1
num_rooms = 1

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

file = open('userlog.txt','w+')

file = open('messagelog.txt','w+')


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
           
            # handle message from the client
            if message[0] == 'login':
                print("[recv] New login request")
                isLoggedIn = self.process_login(messageSaved)
                self.clientSocket.send(isLoggedIn.encode())

            elif message[0] == 'BCM':
                username = message[-1]
                message.remove(username)
                message.remove(message[0])
                
                acknowledge = self.broadcastMessage(message,username)
                self.clientSocket.send(acknowledge.encode())

            elif message[0] == 'ATU':
                username = message[1]
                acknowledge = self.downloadActiveUsers(username)
                print("ack")
                print(acknowledge)
                if isinstance(acknowledge, str) == True:
                    self.clientSocket.send(acknowledge.encode())
                    
                else:
                    data = pickle.dumps(acknowledge)
                    self.clientSocket.send(data)

            elif message[0] == 'SRB':
                username = message[-1]
                message.remove(username)
                message.remove(message[0])
                
                acknowledge = self.seperateRoomBuild(username, message)
                self.clientSocket.send(acknowledge.encode())
            elif message[0] == 'SRM':
                print(message)
            elif message[0] == 'RDM':
                print("[recv] " + message)
            elif message[0] == 'UDP':
                print("[recv] " + message)
            elif message[0] == 'OUT':
                print("[recv] " + message)
            else:
                print("[recv] " + message)
    
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    def process_login(self, message):
        global num_users
        # errorCounter = 0

        # self.clientSocket.send("request username".encode())
        # # self.clientSocket.send("success username".encode())   
        # username = self.clientSocket.recv(1024).decode()
        message = message.split(" ")
        #print(message)
        username = message[1]
        password = message[2]
        port_number = message[3]

        # print("username and password")
        # print(username)
        # print(password)

        for blocked in blocked_users:   
            if username == blocked['username']:
                if time.time() - blocked['time'] > 10:
                    del blocked
                else:
                    return "Your account is blocked due to multiple login failures. Please try again later"
        u_id = num_users
        # check username
        if self.checkPassword(username) == password:
            # process password
            new_user = { "u_id": u_id, "username": username, "password": password, 
            "ip_address": self.clientAddress[0], "port_number": port_number }
            users.append(new_user)
            num_users += 1
            
            info = (str(u_id) + "; " + f"{datetime.datetime.now()}; " + username + "; " + self.clientAddress[0] + "; " + port_number)
            self.writeFile("userlog.txt", info)
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

    def broadcastMessage(self, message, username):
        global num_messages

        m_id = num_messages
        messageBody = ' '.join(message)

        info = (str(m_id) + "; " + f"{datetime.datetime.now()}; " + username + "; " + messageBody)
        self.writeFile("messagelog.txt", info)

        print(username + " broadcasted BCM #" + str(m_id) + " " + messageBody + " at " + f"{datetime.datetime.now()}")
        num_messages += 1

        return "success" + " " + str(m_id) + " " + f"{datetime.datetime.now()}"
    
    def downloadActiveUsers(self, username):
        userList = []
        users = open("userlog.txt", "r")
        for x in users:
            x = x.split("; ")
            if x[2] != username:
                info = (x[2] + " " + x[1] + " " + x[3] + " " + x[4])
                userList.append(info)
        
        print("userList")
        print(userList)

        if len(userList) == 0:
            return "empty list"
        else:
            return userList
    
    def seperateRoomBuild(self, username, message):
        global num_rooms
        global users
        #users = open("userlog.txt", "r")
        checker = 0

        
        r_id = num_rooms
        
        for addUsers in message:
            for active in users:
                if addUsers == active['username']:
                    checker += 1

        
        if checker == len(message):
            test = False
            message.append(username)
            for i in rooms:
                if i['users'] == message:
                    test = True
            
            if test == True:
                return "created" + " " + str(i['r_id'])
            
            new_room = {"r_id": r_id, "users": message, "messages": {}}
            rooms.append(new_room) 
            

            print(rooms)
            self.writeFile(str(num_rooms) + "_messagelog.txt", "")
            num_rooms += 1
            
            return "success" + " " + str(r_id)
        else: 
            
            return "Usernames either don't exist or aren't online"

    def seperateRoomService(self, username, message):
        print("test")
    # def checkUsername(self, username):
    #     f = open("credentials.txt", "r")
    #     userList = f.readlines()

    #     for users in userList:
    #         userInfo = users.split(" ")
    #         if userInfo[0] == username:
    #             return True

    #     return False

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
    
    def writeFile(self, name, info):
        file = open(name, 'a+')
        file.write(info + '\n')
            

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt, invalid_input)
    clientThread.start()

