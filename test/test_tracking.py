from cluster import track, msg

def test_simple_failover():
    """
    This scenario represents a primary/backup configuration. The primary fails
    and the backup takes over.
    """
    backup_state = track.NetState(our_id=2)
    backup_state.incoming(msg.Message(from_id=1, service=1, ip="10.11.0.1",
        mac="00:01:aa:aa:aa:aa", flags=msg.FLAG_ACTIVE | msg.FLAG_SUPPORT))

    # Now the backup has the state information.
    service = backup_state.services[1]
    assert service.ip and service.mac and service.running_on == 1
    assert 1 in backup_state.who_supports[1]

    assert backup_state.tick() == []
    assert backup_state.tick() == []

    result = backup_state.tick()

    # The master missed two checkins for service 1...
    assert len(result) > 0 and result[0][0] == 1

def test_three_client_failover():
    """
    This scenario represents a primary/two backup configuration. The primary
    fails, the backup takes over, and the second backup does nothing.
    """
    b1_state = track.NetState(our_id=2)
    b2_state = track.NetState(our_id=3)

    initial_info = msg.Message(from_id=1, service=1, ip="10.11.0.1",
            mac="00:01:aa:aa:aa:aa", flags=msg.FLAG_ACTIVE | msg.FLAG_SUPPORT)
    b1_state.incoming(initial_info)
    b2_state.incoming(initial_info)

    assert b1_state.services[1].running_on == 1
    assert b2_state.services[1].running_on == 1

    b2_state.incoming(b1_state.services[1].to_supports_message(2))
    b1_state.incoming(b2_state.services[1].to_supports_message(3))

    assert 3 in b1_state.who_supports[1]
    assert 2 in b2_state.who_supports[1]

    b1_state.tick(); b2_state.tick()
    b2_state.incoming(b1_state.services[1].to_supports_message(2))
    b1_state.tick(); b2_state.tick()
    b2_state.incoming(b1_state.services[1].to_supports_message(2))

    # primary has missed two checkins...
    result = b1_state.tick()
    assert len(result) > 0 and result[0][0] == 1

    # but backup 2 should not take over
    result = b2_state.tick()
    assert result == []

def test_three_client_failover_with_two_failures():
    """
    This scenario represents a primary/two backup configuration. The primary
    fails, the secondary fails takes over, and the tertiary takes over.
    """
    b1_state = track.NetState(our_id=2)
    b2_state = track.NetState(our_id=3)

    initial_info = msg.Message(from_id=1, service=1, ip="10.11.0.1",
            mac="00:01:aa:aa:aa:aa", flags=msg.FLAG_ACTIVE | msg.FLAG_SUPPORT)
    b1_state.incoming(initial_info)
    b2_state.incoming(initial_info)

    assert b1_state.services[1].running_on == 1
    assert b2_state.services[1].running_on == 1

    b2_state.incoming(b1_state.services[1].to_supports_message(2))
    b1_state.incoming(b2_state.services[1].to_supports_message(3))

    assert 3 in b1_state.who_supports[1]
    assert 2 in b2_state.who_supports[1]

    b1_state.tick(); b2_state.tick()
    b1_state.tick(); b2_state.tick()

    # primary and backup 1 have both failed
    result = b2_state.tick()
    assert len(result) > 0 and result[0][0] == 1
