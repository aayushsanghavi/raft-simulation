import time
from variables import *
from server import Server
from random import randint
from follower import Follower
from leader import Leader
from threading import Thread
from message import Message
from candidate import Candidate

term = 0
config = {}
available_id = 0

def checkMesages():
    while(True):
        time.sleep(0.0001)
        for name in config:
            if config[name]["object"]._serverState != deadState:
                while(True):
                    message = config[name]["object"].get_message()
                    if message == None:
                        break
                    else:
                        config[name]["object"].on_message(message)

def serverFunction(name):
    server = config[name]["object"]
    if server._serverState == followerState:
        print "Started server with name ", name
    elif server._serverState == resumeState:
        print "Resumed server with name ", name
        print server._commitIndex
        print server._log
        server._state = Follower()
        server._state.set_server(server)
        server._state.on_resume()
        server._serverState = followerState

    while(True):
        if type(server._state) == Leader:
            if time.time() >= server._state._timeoutTime:
                server._state._send_heart_beat()

        if type(server._state) == Candidate and time.time() >= server._state._timeoutTime:
            server._state = Follower()
            server._state.set_server(server)

        if type(server._state) == Follower and term >= 1:
            if time.time() >= server._state._timeoutTime:
                print server._name, "finds that the leader is dead"
                server._serverState = candidateState

        time.sleep(0.0001)
        if server._serverState == deadState:
            print "Killed server with name", name
            server._state = Follower()
            server._state.set_server(server)
            print server._commitIndex
            return

        if server._serverState == candidateState and type(server._state) != Candidate:
            timeout = randint(0.1e5, 5e5)
            timeout = 1.0*timeout/1e6
            time.sleep(timeout)
            if server._serverState == candidateState:
                server._state = Candidate()
                server._state.set_server(server)

print "1. Start a new server"
print "2. Kill a server: name"
print "3. Resume a server: name"
print "4. Client command: name, message_string"
print "5. Initiate first election"

thread = Thread(target=checkMesages, args=())
thread.start()

while(True):
    command = raw_input()
    args = command.split()
    if args[0] == "1":
        state = Follower()
        server = Server(available_id, state, [], [])
        server._total_nodes = available_id + 1
        isLeader = 0
        for i in range(available_id):
            server._neighbors.append(config[i]["object"])
            if type(config[i]["object"]._state) == Leader:
                isLeader = 1
            config[i]["object"]._total_nodes = available_id + 1
            config[i]["object"]._neighbors.append(server)
        if isLeader:
            server._state.on_resume()

        thread = Thread(target=serverFunction, args=(available_id,))
        config[available_id] = {"object": server}
        available_id += 1
        thread.start()
    elif args[0] == "2":
        name = int(args[1])
        config[name]["object"]._serverState = deadState
    elif args[0] == "3":
        name = int(args[1])
        config[name]["object"]._serverState = resumeState
        thread = Thread(target=serverFunction, args=(name,))
        thread.start()
    elif args[0] == "4":
        sender = int(args[1])
        message_data = args[2]
        server = config[sender]["object"]
        server.on_client_command(message_data)
    elif args[0] == "5":
        for i in range(available_id):
            if config[i]["object"]._serverState == followerState:
                config[i]["object"]._serverState = candidateState
        term = 1
