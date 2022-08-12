from ast import main
from asyncio.windows_events import NULL
from http import client
from multiprocessing.spawn import _main
from socket import *
import sys
import pickle
from tkinter.tix import MAIN
from unittest import TestResult
import datetime
from threading import Thread, main_thread

#Server would be running on the same host as Client
if len(sys.argv) != 4:
    print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT UDP_PORT ======\n")
    exit(0)
serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
UDPPort = int(sys.argv[3])
serverAddress = (serverHost, serverPort)
users_UDP = []

class TCPThread(Thread):
    def __init__(self, serverHost, serverPort, serverAddress, UDPPort):
        Thread.__init__(self)
        self.serverHost = serverHost
        self.serverPort = serverPort
        self.serverAddress = serverAddress
        self.UDPPort = UDPPort
        #self.udpThread = udpThread
    
    def run(self):
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect(serverAddress)

        while True:

            username = input("Username: ")
            password = input("Password: ")
            commandRequest = f"login " + username + " " + password + " " + str(serverPort)
            
            clientSocket.send(commandRequest.encode())
            # Waiting for response from server
            response = clientSocket.recv(1024).decode()
            print(response)
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
                            acknowledgeSplit = acknowledge.split(" ", 2) 
                            if acknowledgeSplit[0] == "success":
                                print("#" + acknowledgeSplit[1] + " broadcast at " + acknowledgeSplit[2] )
                            else:
                                print("No ACK received")
                    elif commandRequest == "ATU":
                        if len(commandSize) != 1:
                            print("incorrect ATU argument")
                        else:
                            sending = command + " " + username
                            clientSocket.send(sending.encode())
                            temp = clientSocket.recv(1024)
                            
                            try:
                                
                                acknowledge = temp.decode()
                                acknowledgeSplit = acknowledge.split(" ")
                                
                                if acknowledgeSplit [0] == "empty":
                                    print("no other active user")
                            except:
                                
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
                                users.append(username)
                                
                                print("Seperate chat room has been created, room ID: " + acknowledgeSplit[1] + ", users in this room:" + str(users))
                            elif acknowledgeSplit[0] == "created":
                                print("a separate room (ID:" + acknowledgeSplit[1] + ") already created for these users")
                            else:
                                print("No ACK received")
                    elif commandRequest == "SRM":
                        commandSize2 = command.split(" ", 2)

                        if len(commandSize2) != 3:
                            print("incorrect SRM argument")

                        elif commandSize2[1].isdigit() == False:
                            print("incorrect SRM argument 2")

                        else:
                            sending = command + " " + username
                            clientSocket.send(sending.encode())
                            acknowledge = clientSocket.recv(1024).decode()
                            acknowledgeSplit = acknowledge.split(" ") 
                            
                            if acknowledge == "failed":
                                print("The separate room does not exist")

                            elif acknowledge == "failed2":
                                print("You are not in this separate room chat")

                            elif acknowledge == "success":
                                print(username + " Sent a message ")

                    elif commandRequest == "RDM":
                        commandSize2 = command.split(" ", 2)

                        if len(commandSize2) != 3:
                            print("incorrect RDM argument")

                        elif commandSize2[1] == 'b' or commandSize2[1] == 's':
                            
                            try:
                                timestamp = datetime.datetime.strptime(commandSize2[2], '%d/%m/%y %H:%M:%S')

                                sending = command + " " + username
                                clientSocket.send(sending.encode())
                                ack = clientSocket.recv(1024)

                                if ack == False:
                                    print("no new message")
                                else:
                                    lister = pickle.loads(ack)
                                    print(lister)
                                
                            except:
                                print("incorrect datetime message")
                        else:
                            print("incorrect RDM argument 2")
                            

                    elif commandRequest == "UPD":
                        commandSize2 = command.split(" ")
                        if len(commandSize2) != 3:
                            print("incorrect UPD argument")
                        else:
                            targetUser = commandSize2[1]
                            file = commandSize2[2]
                            print(targetUser)
                            print(file)
                    elif commandRequest == "OUT":
                        if len(commandSize) != 1:
                            print("incorrect OUT argument")
                        else:
                            sending = command + " " + username
                            clientSocket.send(sending.encode())
                            acknowledge = clientSocket.recv(1024).decode()
                            if acknowledge == "success":
                                print("bye bye :(")
                                clientSocket.close()
                                quit()
                            elif acknowledge == "fail":
                                print("no ack")
                    else:
                        print("Error. Invalid Command!")
        clientSocket.close()
            
            
            
# class UDPThread(Thread):
#     def __init__(self, serverHost, UDPSocket):
#         Thread.__init__(self)
#         self.serverHost = serverHost
#         self.UDPSocket = UDPSocket
# while True:
#     files = clientSocket.recv(1024)
#     #def run(self):
#         #while 1:
if __name__ == "__main__":
    # UDPclientSocket = socket(AF_INET, SOCK_DGRAM)
    # UDPclientSocket.bind((serverHost, UDPPort))
    # udpThread = UDPThread(serverHost, UDPclientSocket)
    # udpThread.start()
    clientThread = TCPThread(serverHost, serverPort, serverAddress, UDPPort)
    clientThread.start()
