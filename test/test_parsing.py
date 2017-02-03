from cluster import msg

def test_message_parsing():
    sample = msg.Message(42, 424242, "42.43.44.45", "42:43:44:45:46:47", 2)
    assert msg.parse(msg.unparse(sample)) == sample

def test_ip_conversion():
    for i in ("0.0.0.0", "255.255.255.255", "10.11.0.14"):
        assert msg.int_to_octets(msg.octets_to_int(i)) == i

def test_mac_conversion():
    for i in ("00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff", "ab:cd:ef:12:34:56"):
        assert msg.bytes_to_mac(msg.mac_to_bytes(i)) == i
