from sphinxmix.SphinxParams import SphinxParams
from sphinxmix.SphinxClient import Nenc, create_forward_message, pack_message, rand_subset

import asyncio

from argparse import ArgumentParser

from init_mix import public_key_from_str

arg_parser = ArgumentParser()
arg_parser.add_argument('-c', '--mix-client-config', default='temp/mix_client_config.csv')
arg_parser.add_argument('-d', '--destination', default='bob@bestmail.com')
arg_parser.add_argument('-m', '--message', default='00000000000000000000000000000000000000000')
arg_parser.add_argument('-r', '--num-path-nodes', default=2, type=int)
args = arg_parser.parse_args()

mix_network_filename = args.mix_client_config
destination = args.destination
message = args.message
num_path_nodes = args.num_path_nodes

params = SphinxParams()
param_dict = { (params.max_len, params.m): params }
id_to_mix_node = dict()

mix_network_file = open(mix_network_filename)

for line in mix_network_file.readlines():
    line = line[:-1]
    split_line = line.split(',')

    node_id = int(split_line[0])

    node_host = split_line[1]
    node_port = int(split_line[2])
    node_public_key = public_key_from_str(split_line[3], params.group.G)

    id_to_mix_node[node_id] = (node_host, node_port, node_public_key)

mix_network_file.close()


async def send_mix_message(message, destination, first_mix_id, nodes_routing, keys_nodes, loop):
    first_mix_host, first_mix_port, _ = id_to_mix_node[first_mix_id]
    _, writer = await asyncio.open_connection(first_mix_host, first_mix_port, loop=loop)

    header, delta = create_forward_message(params, nodes_routing, keys_nodes, destination, message)
    packed_message = pack_message(params, (header, delta))

    writer.write(packed_message)
    await writer.drain()
    writer.close()


use_nodes = rand_subset(list(id_to_mix_node.keys()), num_path_nodes)
nodes_routing = list(map(Nenc, use_nodes))
keys_nodes = [id_to_mix_node[n][2] for n in use_nodes]

loop = asyncio.new_event_loop()
loop.run_until_complete(send_mix_message(message.encode(), destination.encode(), use_nodes[0], nodes_routing, keys_nodes, loop))
loop.close()
