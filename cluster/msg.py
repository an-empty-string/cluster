import collections
import struct

Message = collections.namedtuple("Message", ["from_id", "service", "ip", "mac", "flags"])
class BadMagic(Exception): pass

MAGIC = bytes([167, 53, 46, 90, 215, 14, 202, 202, 131, 197, 245, 125, 47])

FLAG_ACTIVE = 1
FLAG_SUPPORT = 2

def int_to_octets(i):
    """
    Convert a 32-bit integer to an IPv4 address in dotted-octet notation.
    """
    octets = []
    for _ in range(4):
        octets.append(i % 256)
        i //= 256
    return ".".join(map(str, reversed(octets)))

def octets_to_int(s):
    """
    Convert an IPv4 address in dotted-octet notation to a 32-bit integer.
    """
    result = 0
    for i in s.split("."):
        result *= 256
        result += int(i)
    return result

def bytes_to_mac(by):
    """
    Convert a bytestring to a mac address in :-delimited format.
    """
    return ":".join(hex(i)[2:].zfill(2) for i in by)

def mac_to_bytes(mac):
    """
    Convert a : delimited mac address to a bytestring.
    """
    return bytes(int(i, 16) for i in mac.split(":"))

def parse(by):
    """
    Parse a message from the wire.
    """
    magic, from_id, service, ip, mac, flags = struct.unpack(">13sIII6sB", by)
    if magic != MAGIC:
        raise BadMagic()
    return Message(from_id, service, int_to_octets(ip), bytes_to_mac(mac), flags)

def unparse(msg):
    """
    "Unparse" a message before sending it over the wire.
    """
    return struct.pack(">13sIII6sB", MAGIC, msg.from_id, msg.service,
            octets_to_int(msg.ip), mac_to_bytes(msg.mac), msg.flags)
