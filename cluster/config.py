import yaml
class ClusterConfig:
    def __init__(self, fname):
        with open(fname) as f:
            config = yaml.load(f)
            self.id = config["id"]
            self.bcast = config["bcast"]
            self.services = [ServiceConfig(i) for i in config["services"]]

class ServiceConfig:
    def __init__(self, config):
        self.id = config["id"]
        self.dev = config["dev"]
        self.ip = None
        self.mac = None
