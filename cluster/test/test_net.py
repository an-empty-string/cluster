import select
import socket
import threading
import types
from cluster import net, msg

class MockSocket:
    def __init__(self, domain=socket.AF_INET, stype=socket.SOCK_STREAM):
        self.domain = domain
        self.stype = stype
        self.blocking = 1
        self.bound = None
        self.opts = {}

        self.last_to = None
        self.last_message = None

        self.buffer = b""

    def bind(self, t):
        if self.bound:
            raise Exception("Cannot rebind")

        self.bound = t

    def setblocking(self, t):
        self.blocking = t

    def setsockopt(self, level, optname, value):
        self.opts[(level, optname)] = value

    def sendto(self, msg, dest):
        self.last_message = msg
        self.last_to = dest

    def recv(self, n=32):
        ret = self.buffer[:n]
        self.buffer = self.buffer[n:]
        return ret

class MockThread:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.started = False

    def start(self):
        self.started = True

def test_net_listen(monkeypatch):
    monkeypatch.setattr(socket, "socket", MockSocket)
    monkeypatch.setattr(threading, "Thread", MockThread)
    monkeypatch.setattr(select, "select", lambda r, w, o: None)

    last_data = None

    config = types.SimpleNamespace(bcast="10.0.0.255")
    l = net.Listener(config)

    last_data = []
    def callback(x):
        last_data.append(x)
        l.running = False

    l.listen(callback)

    assert l.sock.domain == socket.AF_INET
    assert l.sock.stype == socket.SOCK_DGRAM
    assert l.sock.bound == ("10.0.0.255", net.PORT)
    assert not l.sock.blocking
    assert l.thread.started
    assert l.running

    sample = msg.Message(1, 1, "1.1.1.1", "11:11:11:11:11:11", 1)
    l.sock.buffer = msg.unparse(sample)
    l._listen(callback)
    assert last_data[-1] == sample

    sample2 = msg.Message(2, 2, "1.1.1.2", "11:11:12:11:12:11", 1)
    l.sock.buffer = b"\x42" + msg.unparse(sample2)
    l.running = True
    l._listen(callback)
    assert last_data[-1] == sample2

def test_net_send(monkeypatch):
    monkeypatch.setattr(socket, "socket", MockSocket)

    config = types.SimpleNamespace(bcast="10.0.0.255")
    b = net.Broadcaster(config)

    assert b.sock.opts[(socket.SOL_SOCKET, socket.SO_BROADCAST)] == 1
    assert not b.sock.bound
    assert b.sock.domain == socket.AF_INET
    assert b.sock.stype == socket.SOCK_DGRAM

    sample = msg.Message(1, 1, "1.1.1.1", "11:11:11:11:11:11", 1)
    b.send(sample)

    assert b.sock.last_to == ("10.0.0.255", net.PORT)
    assert b.sock.last_message == msg.unparse(sample)
