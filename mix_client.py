#!venv/bin/python3

from sphinxmix.SphinxParams import SphinxParams
from sphinxmix.SphinxClient import Nenc, create_forward_message, pack_message, rand_subset

import sys
import asyncio

from init_mix import public_key_from_str

params = SphinxParams()
param_dict = { (params.max_len, params.m): params }

port_to_public_key = dict()

mix_network_filename = sys.argv[1]
destination = sys.argv[2]
message = sys.argv[3]

if len(sys.argv) >= 5:
    num_path_nodes = int(sys.argv[4])
else:
    num_path_nodes = 2

mix_network_file = open(mix_network_filename)

for line in mix_network_file.readlines():
    line = line[:-1]
    split_line = line.split(',')

    port = int(split_line[0])
    public_key = public_key_from_str(split_line[1], params.group.G)
    port_to_public_key[port] = public_key

mix_network_file.close()


async def send_mix_message(message, destination, first_mix_port, nodes_routing, keys_nodes, loop):
    _, writer = await asyncio.open_connection('127.0.0.1', first_mix_port, loop=loop)

    header, delta = create_forward_message(params, nodes_routing, keys_nodes, destination, message)
    packed_message = pack_message(params, (header, delta))

    writer.write(packed_message)
    await writer.drain()
    writer.close()


use_nodes = rand_subset(list(port_to_public_key.keys()), num_path_nodes)
nodes_routing = list(map(Nenc, use_nodes))
keys_nodes = [port_to_public_key[n] for n in use_nodes]

loop = asyncio.new_event_loop()
loop.run_until_complete(send_mix_message(message.encode(), destination.encode(), use_nodes[0], nodes_routing, keys_nodes, loop))
loop.close()
