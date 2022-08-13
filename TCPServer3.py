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
    
]
'''
blocked_users = []
server_messages = []
rooms = []
num_messages = 1
room_num_messages = 1
num_users = 1
num_rooms = 1
BUFF_SIZE = 65536

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
                print("===== the user disconnected ====", self.clientAddress)
                break
            messageSaved = message
            message = message.split(" ")
           
            # handle message from the client
            if message[0] == 'login':
                
                isLoggedIn = self.process_login(messageSaved)
                self.clientSocket.send(isLoggedIn.encode())

            elif message[0] == 'BCM':
                username = message[-1]
                message.remove(message[-1])
                message.remove(message[0])
                
                acknowledge = self.broadcastMessage(message,username)
                self.clientSocket.send(acknowledge.encode())

            elif message[0] == 'ATU':
                print(message)
                username = message[1]
                udp_Port = message[2]
                
                acknowledge = self.downloadActiveUsers(username, udp_Port)
                
                print("ATU Return Message: " + f'{acknowledge}')
                
                if isinstance(acknowledge, str) == True:
                    self.clientSocket.send(acknowledge.encode())
                    
                    
                else:
                    data = pickle.dumps(acknowledge)
                    self.clientSocket.send(data)
                    

            elif message[0] == 'SRB':
                username = message[-1]
                message.remove(message[-1])
                message.remove(message[0])
                print(username + " issued SRB command")
                
                acknowledge = self.seperateRoomBuild(username, message)
                self.clientSocket.send(acknowledge.encode())

            elif message[0] == 'SRM':
                username = message[-1]
                message.remove(message[-1])
                message.remove(message[0])

                acknowledge = self.seperateRoomMessage(username, message)
                
                self.clientSocket.send(acknowledge.encode())
            elif message[0] == 'RDM':
                username = message[-1]
                message.remove(message[-1])
                message.remove(message[0])
        
                acknowledge = self.readMessage(username, message)
                data = pickle.dumps(acknowledge)
                self.clientSocket.send(data)

            elif message[0] == 'UDP':
                print("[recv] " + message)
            elif message[0] == 'OUT':
                print(message[1] + " logout")
                username = message[1]
                acknowledge = self.logOut(username)
                self.clientSocket.send(acknowledge.encode())
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
        
        message = message.split(" ")
        
        username = message[1]
        password = message[2]
        port_number = message[3]

        
        for blocked in blocked_users:   
            if username == blocked['username']:
                if time.time() - blocked['time'] > 10:
                    blocked_users.remove(blocked)
                else:
                    return "Your account is blocked due to multiple login failures. Please try again later"
        u_id = num_users
        # check username
        if self.checkPassword(username) == password:
            # process password
            new_user = { "u_id": u_id, "username": username, "password": password, 
            "ip_address": self.clientAddress[0], "port_number": port_number, "time": datetime.datetime.now()}
            users.append(new_user)
            num_users += 1
            
            info = (str(u_id) + "; " + f"{datetime.datetime.now()}; " + username + "; " + self.clientAddress[0] + "; " + port_number)
            self.writeFile("userlog.txt", info, False)
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
        self.writeFile("messagelog.txt", info, False)

        new_message = {"m_id": m_id, "user": username, "time": datetime.datetime.now(), "message": messageBody}

        server_messages.append(new_message)


        print(username + " broadcasted BCM #" + str(m_id) + " " + messageBody + " at " + f"{datetime.datetime.now()}")
        num_messages += 1

        return "success" + " " + str(m_id) + " " + f"{datetime.datetime.now()}"
    
    def downloadActiveUsers(self, username, udp_Port):
        userList = []
        
        #users = open("userlog.txt", "r")
        for x in users:
            #x = x.split("; ")
            if x['username'] != username:
                info = (x['username'] + ", " + f"{x['time']}" + ", " + x['ip_address'] + ", " + udp_Port)
                userList.append(info)

        if len(userList) == 0:
            return "empty list"
        else:
            return userList
    
    def seperateRoomBuild(self, username, message):
        global num_rooms

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
            
            new_room = {"r_id": r_id, "users": message, "messages": []}
            rooms.append(new_room) 
            print("Seperate chat room has been created, room ID:" + str(r_id) + ", users in this room:" + f'{message}')
            # print("1")
            # print(rooms)
            self.writeFile("SR_" + str(num_rooms) + "_messagelog.txt", "", True)
            num_rooms += 1
            
            return "success" + " " + str(r_id)
        else: 
            
            return "Usernames either don't exist or aren't online"

    def seperateRoomMessage(self, username, message):
        global room_num_messages
        
        r_id = message[0]
        message.remove(message[0])
        messageBody = ' '.join(message)
        

        info = (str(room_num_messages) + "; " + f"{datetime.datetime.now()}; " + username + "; " + messageBody)
        checker = False
        userInRoom = False
        for i in rooms:
            if i['r_id'] == int(r_id):
                checker = True
                for x in i['users']:
                    if username == x:
                        print("#" + str(room_num_messages) + "; " + f'{datetime.datetime.now()}' + "; " + username + "; " + str(message))
                        new_message = {"m_id": str(room_num_messages), "user": username, "time": datetime.datetime.now(), "message": messageBody}
                        i['messages'].append(new_message)
                        self.writeFile("SR_" + r_id + "_messagelog.txt", info, False)
                        room_num_messages += 1
                        # print("2")
                        # print(rooms)
                        return "success"
                if userInRoom == False:
                    return "failed2"
        
        if checker == False:
            return "failed"
    
    def readMessage(self, username, message):
        messageType = message[0]
        message.remove(message[0])
        sendMessage = []
        
        time = ' '.join(message)
        timestamp = datetime.datetime.strptime(time, '%d/%m/%y %H:%M:%S')
        

        if messageType == 'b':
            for i in server_messages:
                
                if i['time'] > timestamp:
                    m_id = i['m_id']
                    BCM_user = i['user']
                    BCM_time = i['time']
                    BCM_message = i['message']

                    info = BCM_user + " broadcasted BCM #" + str(m_id) + " " + BCM_message + " at " + f"{BCM_time}"
                    sendMessage.append(info)

        elif messageType == 's':
            for i in rooms:
                
                if username in i['users']:
                    
                    for j in i['messages']:
                        
                        if j['time'] > timestamp:
                            m_id = j['m_id']
                            SRM_user = j['user']
                            SRM_time = j['time']
                            SRM_message = j['message']
                            
                            info = "room #:" + str(i['r_id']) + " #" + str(m_id) + "; " + SRM_user + " broadcasted: " + SRM_message + " at " + f"{SRM_time}"
                            sendMessage.append(info)
                            
        return sendMessage
    
    def logOut(self,username):
        #print(users)
        for x in users:
            
            if x['username'] == username:
                
                users.remove(x)
                file = open('userlog.txt','r')
                lines = file.readlines()
                file.close()
                
                file = open('userlog.txt','w')
                for line in lines:
                    line_user = line.split("; ")
                    if line_user[2] != username:
                        file.write(line)
                return "success"
        
        return "fail"
                
                
        
        

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
    
    def writeFile(self, name, info, reset):
        if reset == True:
            file = open(name,'w+')
        else:
            file = open(name, 'a+')
            file.write(info + '\n')
            

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt, invalid_input)
    clientThread.start()

