from asyncio.windows_events import NULL
from http import client
from socket import *
import sys
import pickle
from unittest import TestResult

#Server would be running on the same host as Client
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT ======\n")
    exit(0)
serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
serverAddress = (serverHost, serverPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# build connection with the server and send message to it
clientSocket.connect(serverAddress)
while True:


    # if clientSocket.recv(1024).decode() == "request username":
        
    #     #server = clientSocket.recv(1024).decode()
    #     username = input("Username: ")
    #     clientSocket.send(username.encode())

    #     if clientSocket.recv(1024).decode() == "blocked user":
    #         print("blocked test")

    # if clientSocket.recv(1024).decode() == "request password":
    #     #server = clientSocket.recv(1024).decode()
    #     password = input("Password: ")
    #     clientSocket.send(password.encode())
    #     hans falcon*solo  yoda wise@!man

    username = input("Username: ")
    password = input("Password: ")
    commandRequest = f"login " + username + " " + password + " " + str(serverPort)
    
    clientSocket.send(commandRequest.encode())
    # Waiting for response from server
    response = clientSocket.recv(1024).decode()
    if (response == "success"):
        print("Ive successfully logged in")
        while True:
            command = input("Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT, UPD):")
            
            commandRequest = command.split(" ", 1)[0]
            commandSize = command.split(" ", 1)
           
            if commandRequest == "BCM":
                if len(commandSize) != 2:
                    print("incorrect BCM argument")
                else:
                    sending = command + " " + username
                    clientSocket.send(sending.encode())
                    acknowledge = clientSocket.recv(1024).decode()
                    acknowledgeSplit = acknowledge.split(" ") 
                    if acknowledgeSplit[0] == "success":
                        print("#" + acknowledgeSplit[1] + " broadcast at " + acknowledgeSplit[2])
                    else:
                        print("No ACK received")
            elif commandRequest == "ATU":
                if len(commandSize) != 1:
                    print("incorrect ATU argument")
                else:
                    sending = command + " " + username
                    clientSocket.send(sending.encode())
                    temp = clientSocket.recv(1024)
                    
                    if isinstance(temp, bytes) == True:
                        
                        acknowledge = temp.decode()
                        acknowledgeSplit = acknowledge.split(" ")
                        
                        if acknowledgeSplit [0] == "empty":
                            print("no other active user")
                    else:
                        
                        lister = pickle.loads(temp)
                        print(lister) 
                    
            elif commandRequest == "SRB":
                if len(commandSize) != 2:
                    print("incorrect SRB argument")
                else:
                    sending = command + " " + username
                    clientSocket.send(sending.encode())
                    acknowledge = clientSocket.recv(1024).decode()
                    acknowledgeSplit = acknowledge.split(" ") 
                    print(acknowledge)
                    
                    if acknowledgeSplit[0] == "success":
                        print(command)
                        users = command.split(" ")
                        users.remove(users[0])
                        
                        print("Seperate chat room has been created, room ID: " + acknowledgeSplit[1] + ", users in this room:" + str(users))
                    elif acknowledgeSplit[0] == "created":
                        print("a separate room (ID: " + acknowledgeSplit[1] + ") already created for these users")
                    else:
                        print("No ACK received")
            elif commandRequest == "SRM":
                commandSize2 = command.split(" ", 2)
                print(commandSize2[1])
                if len(commandSize2) != 3:
                    print("incorrect SRB argument")
                elif commandSize2[1].isdigit() == False:
                    print("incorrect SRB argument")
                else:
                    sending = command + " " + username
                    clientSocket.send(sending.encode())
            elif commandRequest == "RDM":
                print("[send] Cannot understand this message")
            elif commandRequest == "OUT":
                print("[send] Cannot understand this message")
            else:
                print("Error. Invalid Command!")


    else:
        print(response)


    # clientSocket.send(username.encode())

# close the socket
clientSocket.close()
