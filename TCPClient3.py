from http import client
from socket import *
import sys

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

    username = input("Username: ")
    password = input("Password: ")
    commandRequest = f"login " + username + " " + password
    print("test")
    print(commandRequest)
    clientSocket.send(commandRequest.encode())
    # Waiting for response from server
    response = clientSocket.recv(1024).decode()
    if (response == "success"):
        print("Ive successfully logged in")
        while True:
            command = input("===== Please type any messsage you want to send to server: =====\n")
            #commandRequest = command.split(" ", 1)
            clientSocket.send(command.encode())

    else:
        print(response)


    # clientSocket.send(username.encode())

# close the socket
clientSocket.close()
