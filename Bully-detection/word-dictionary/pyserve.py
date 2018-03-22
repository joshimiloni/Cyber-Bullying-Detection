#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import string
# from pyserve import *

# print(msg)
badwords = []
for line in open("badwords.txt"):
    for word in line.split( ):
        badwords.append(word)



def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    # print(msg)
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        msgString = msg.decode('utf-8')
        print (msgString)
        print(str(msgString.split(" ")))
        print("clients",clients[client])
        bullying = False
        for word in msgString.split(" "):
            if word in badwords:
                print ("bullying")
                # broadcast(bytes(msg, "utf8"))
                broadcast(bytes("%s, Stop bullying people and behave decently. If you do this again we will block you." % name, "utf8"))
                
                # api.update_status("@" + status.author.screen_name+"\n You should stop bullying people. (I am a bot in testing, don't take this too seriously)", status.id)
                bullying = True
                break
        if bullying == False:
            # api.update_status("\n Good job, you're not a bully! (I am a bot in testing, don't take this too seriously)", status.id)
            # broadcast(bytes(msg, "utf8"))
            print ("not bullying")
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

        
clients = {}
addresses = {}

HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
# SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()