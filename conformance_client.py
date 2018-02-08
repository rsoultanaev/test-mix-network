from sphinxmix.SphinxClient import *
from sphinxmix.SphinxParams import SphinxParams
from sphinxmix.SphinxNode import sphinx_process

from petlib.bn import Bn
from petlib.ec import EcPt 

from base64 import b64decode

from struct import pack, unpack

import sys


def parse_args(args, sphinx_params):
    dest = b64decode(args[0])
    message = b64decode(args[1])

    nodes_routing = []
    node_keys = []
    for node_key_pair in args[2:]:
        node_str, key_str = node_key_pair.split(':')

        node = Nenc(pack('b', int(node_str)))
        key = EcPt.from_binary(b64decode(key_str), sphinx_params.group.G)

        nodes_routing.append(node)
        node_keys.append(key)

    return dest, message, nodes_routing, node_keys


def create_sphinx_packet(sphinx_params, dest, message, nodes_routing, node_keys):
    header, delta = create_forward_message(sphinx_params, nodes_routing, node_keys, dest, message)
    return pack_message(sphinx_params, (header, delta))


if __name__ == "__main__":
    sphinx_params = SphinxParams()
    dest, message, nodes_routing, node_keys = parse_args(sys.argv[1:], sphinx_params)
    bin_message = create_sphinx_packet(sphinx_params, dest, message, nodes_routing, node_keys)
    sys.stdout.buffer.write(bin_message)

