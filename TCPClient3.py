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
from time import sleep
import os


#Server would be running on the same host as Client
if len(sys.argv) != 4:
    print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT UDP_PORT ======\n")
    exit(0)
serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
UDPPort = int(sys.argv[3])
serverAddress = (serverHost, serverPort)
users_UDP = []
BUFF_SIZE = 65536
 
class TCPThread(Thread):
    def __init__(self, serverHost, serverPort, serverAddress, UDPPort, udpThread):
        Thread.__init__(self)
        self.serverHost = serverHost
        self.serverPort = serverPort
        self.serverAddress = serverAddress
        self.UDPPort = UDPPort
        self.udpThread = udpThread
    
    def run(self):
        global users_UDP
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect(serverAddress)

        while True:

            username = input("Username: ")
            password = input("Password: ")
            commandRequest = f"login " + username + " " + password + " " + str(serverPort) + " "
            
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
                        users_UDP = []
                        if len(commandSize) != 1:
                            print("incorrect ATU argument")
                        else:
                            sending = command + " " + username + " " + str(UDPPort)
                            clientSocket.send(sending.encode())
                            temp = clientSocket.recv(1024)
                            
                            try:
                                
                                acknowledge = temp.decode()
                                acknowledgeSplit = acknowledge.split(" ")
                                
                                if acknowledgeSplit [0] == "empty":
                                    print("no other active user")
                            except:
                                
                                lister = pickle.loads(temp)
                                for x in lister:
                                    x = x.split(", ")
                                    info = {'username': x[0], 'ip_address': x[2], 'udp_Port': x[3] }
                                    users_UDP.append(info)
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

                            userActive = False
                            for i in users_UDP:
                                if i['username'] == targetUser:
                                    userActive = True
                                    targetUserAddress = i['ip_address']
                                    targetUserUDPPort = i['udp_Port']

                                    #acknowledge = self.udpSenderFunction(targetUser, username, file, targetUserAddress, targetUserUDPPort)
                                    
                                    try:
                                        print("hello")
                                        acknowledge = self.udpSenderFunction(targetUser, file, targetUserAddress, targetUserUDPPort)
                                        print("acknowledge")
                                        print(acknowledge)
                                        if acknowledge == "success":
                                            print(file + " has been sent to " + targetUser)
                                        else:
                                            print("fail UPD acknowledge")
                                    except:
                                        print("filename error")
                                    
                            if userActive == False      :
                                print("User: " + targetUser + " either doesnt exist or is offline")
                            
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
        quit()

    def udpSenderFunction(self,targetUser, file, targetUserAddress, targetUserUDPPort):     
        
        clientSocket = socket(AF_INET, SOCK_DGRAM) 
        
        data = f'{targetUser} {file}'
        clientSocket.sendto(data.encode(),(targetUserAddress,int(targetUserUDPPort)))
        
        f = open(file, "rb")   
        vid = f.read(1024)

        while vid:
            
            clientSocket.sendto(vid,(targetUserAddress,int(targetUserUDPPort)))
            vid = f.read(1024)
            sleep(0.001)

        f.close()
        clientSocket.close()
        return 'success'
class UDPThread(Thread):
    def __init__(self, serverHost, UDPSocket):
        Thread.__init__(self)
        self.serverHost = serverHost
        self.UDPSocket = UDPSocket
    
    def run(self):
        
        while True:
            files = self.UDPSocket.recv(1024).decode()
            files = files.split()

            if os.path.exists(f'./{files[0]}') == False:
                os.makedirs(f'./{files[0]}')


            f = open(f"./{files[0]}/{files[1]}", "wb")
            video = self.UDPSocket.recv(1024)

            try:
                while video:
                    f.write(video)
                    video = self.UDPSocket.recv(1024)
            except:
                
                f.close()


if __name__ == "__main__":
    UDPSocket = socket(AF_INET, SOCK_DGRAM)
    UDPSocket.bind((serverHost, UDPPort))
    udpThread = UDPThread(serverHost, UDPSocket)
    udpThread.start()
    clientThread = TCPThread(serverHost, serverPort, serverAddress, UDPPort, udpThread)
    clientThread.start()
