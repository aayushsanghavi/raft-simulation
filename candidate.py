import time
from random import randint
from variables import *
from voter import Voter
from leader import Leader
from follower import Follower
from message import Message

class Candidate(Voter):
    def set_server(self, server):
        self._server = server
        self._votes = {}
        self._start_election()

    def on_vote_request(self, message):
        return self, None

    def on_vote_received(self, message):
        self._votes[message.sender] = message
        if len(self._votes.keys()) >= (self._server._total_nodes - 1) / 2:
            leader = Leader()
            leader.set_server(self._server)
            print "Server", self._server._name, "has been elected leader"
            self._server._serverState = leaderState
            for n in self._server._neighbors:
                if n._serverState != deadState:
                    n._serverState = followerState
                    n._state = Follower()
                    n._state.set_server(n)
            return leader, None

        return self, None

    def _start_election(self):
        print self._server._name, "is starting election"
        self._timeoutTime = time.time() + (randint(1e6, 2e6)*1.0)/1e6
        self._votes = {}
        self._server._currentTerm += 1
        election = Message(
            self._server._name,
            None,
            self._server._currentTerm,
            {
                "lastLogIndex": self._server._lastLogIndex,
                "lastLogTerm": self._server._lastLogTerm,
            }, Message.RequestVote)

        self._server.send_message(election)
        self._last_vote = self._server._name
