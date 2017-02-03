from . import msg
import select
import socket
import threading

PORT = 60743

class Listener:
    """
    A broadcast message listener. Binds to the broadcast address given in the
    specified configuration.
    """
    def __init__(self, config):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((config.bcast, PORT))
        self.sock.setblocking(0)

    def listen(self, callback):
        """
        Start the listener thread. Parsed messages will be sent to the given
        callback function.
        """
        threading.Thread(target=self._listen, args=(callback,)).start()

    def _listen(self, handler):
        buf = b""
        while True:
            result = select.select([self.sock], [], [])
            data = self.sock.recv(32)
            buf += data
            while len(buf) >= 32 and msg.MAGIC in buf:
                pos = buf.find(msg.MAGIC)
                if pos == 0:
                    handler(msg.parse(buf[:32]))
                    buf = buf[32:]
                else:
                    buf = buf[pos:]

class Broadcaster:
    """
    A broadcast message sender.
    """
    def __init__(self, config):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.config = config

    def send(self, mesg):
        """
        Send a broadcast message after unparsing.
        """
        self.sock.sendto(msg.unparse(mesg), (self.config.bcast, PORT))
