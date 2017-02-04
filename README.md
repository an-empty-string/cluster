# Lessbroken Cluster

[![Build Status](https://travis-ci.org/lessbroken/cluster.svg?branch=master)](https://travis-ci.org/lessbroken/cluster)
[![Code Climate](https://codeclimate.com/github/lessbroken/cluster/badges/gpa.svg)](https://codeclimate.com/github/lessbroken/cluster)

Lessbroken Cluster is a clustering engine specifically designed to handle
failover of dynamic IPs.

## Requirements

The most obvious requirement is an IP address for failover.

Machines talking in a cluster need a dedicated network for cluster coordination.
They'll be broadcasting announcements on this network in order to keep track of
the overall state of the network. It's okay to reuse this network for multiple
failover IPs.

You'll need to assign an ID for each IP you wish to provide clustering services
for. It must be unique on the cluster management network.

You'll also need to assign each machine an ID. The machine with the lowest ID
that is configured to bring up an IP, and is actually up, will be the machine
which takes the IP.

All machines configured to pick up an IP must be ready to do so at all times.
There's currently no facility for i.e. starting a service before failover.
