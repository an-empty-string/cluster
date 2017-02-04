from . import net, msg
from .msg import FLAG_ACTIVE, FLAG_SUPPORT
import collections

TICK = 5 # seconds, outages will be detected and corrected within TICK * 3 seconds
MAX_AGE = 3

class ServiceState:
    def __init__(self):
        self.service = 0
        self.running_on = None
        self.ip = "0.0.0.0"
        self.mac = "00:00:00:00:00:00"
        self.age = 0

    def to_supports_message(self, my_id):
        return msg.Message(from_id=my_id, service=self.service, ip=self.ip,
                mac=self.mac, flags=FLAG_SUPPORT)

class NetState:
    def __init__(self, our_id):
        self.our_id = our_id
        self.services = collections.defaultdict(ServiceState)
        self.who_supports = collections.defaultdict(lambda: collections.defaultdict(int))
        self.running = set()

    def tick(self):
        for k, v in self.services.items():
            v.age += 1

        for _, v in self.who_supports.items():
            # v is a dict[hostid, age]
            to_remove = set()
            for k in v:
                v[k] += 1
                if v[k] >= MAX_AGE:
                    to_remove.add(k)
            for k in to_remove:
                v.pop(k)

        # it's a service we know about,
        # have enough configuration data for and is too old,
        # and isn't someone else's problem
        return [(k, v) for k, v in self.services.items()
                if v.ip and v.mac and v.age >= MAX_AGE and
                (not self.who_supports[k] or
                    min(self.who_supports[k].keys()) >= self.our_id)]

    def incoming(self, message):
        if message.flags & msg.FLAG_ACTIVE:
            state = self.services[message.service]
            state.service = message.service
            state.age = 0
            state.running_on = message.from_id
            state.ip = message.ip
            state.mac = message.mac

        if message.flags & msg.FLAG_SUPPORT:
            self.who_supports[message.service][message.from_id] = 0
