import time

class Message(object):
    AppendEntries = 0
    RequestVote = 1
    RequestVoteResponse = 2
    Response = 3
    ClientCommand = 4

    def __init__(self, sender, receiver, term, data, message_type):
        self._timestamp = int(time.time())
        self._sender = sender
        self._receiver = receiver
        self._data = data
        self._term = term
        self._type = message_type

    @property
    def receiver(self):
        return self._receiver

    @property
    def sender(self):
        return self._sender

    @property
    def data(self):
        return self._data

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def term(self):
        return self._term

    @property
    def type(self):
        return self._type
