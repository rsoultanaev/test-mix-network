from petlib.bn import Bn
from petlib.ec import EcPt 

from sphinxmix.SphinxParams import SphinxParams

from binascii import hexlify, unhexlify

import sys
import subprocess
import os
import os.path
import socket

from argparse import ArgumentParser

def public_key_to_str(public_key):
    return hexlify(public_key.export()).decode('utf-8')

def public_key_from_str(public_key_string, ecpt_group):
    public_key_byte_string = unhexlify(public_key_string.encode('utf-8'))
    return EcPt.from_binary(public_key_byte_string, ecpt_group)

def init_mix_network(num_servers, temp_folder, use_existing_config, server_public_host):
    params = SphinxParams()
    mix_nodes_filename = os.path.join(temp_folder, 'mix_node_config.csv')
    client_config_filename = os.path.join(temp_folder, 'mix_client_config.csv')

    base_id = 0
    server_ids = [str(base_id + i) for i in range(num_servers)]

    base_port = 8000
    server_ports = [str(base_port + i) for i in range(num_servers)]

    server_host = '0.0.0.0'

    if not use_existing_config:
        private_keys = [params.group.gensecret() for i in range(num_servers)]

        mix_node_config_lines = []
        mix_client_config_lines = []
        for i in range(len(private_keys)):
            public_key = params.group.expon(params.group.g, private_keys[i])
            private_key_str = str(private_keys[i])
            public_key_str = public_key_to_str(public_key)
            mix_node_config_lines.append(','.join([server_ids[i], server_host, server_ports[i], public_key_str, private_key_str]))
            mix_client_config_lines.append(','.join([server_ids[i], server_public_host, server_ports[i], public_key_str]))

        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        output_file = open(mix_nodes_filename, 'w')

        for line in mix_node_config_lines:
            output_file.write(line + '\n')

        output_file.close()

        output_file = open(client_config_filename, 'w')

        for line in mix_client_config_lines:
            output_file.write(line + '\n')

        output_file.close()

    for i in range(num_servers):
        server_id = server_ids[i]
        server_port = server_ports[i]
        subprocess.Popen('python3 mix_server.py -i {} -a {} -p {} -f {} -t {}'.format(server_id, server_host, server_port, mix_nodes_filename, temp_folder), shell=True)
        print('Started server on:', server_port)

if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-n', '--num-servers', type=int, default=3)
    arg_parser.add_argument('-t', '--temp-folder', default='temp')
    arg_parser.add_argument('-a', '--server-public-host', default='127.0.0.1')
    arg_parser.add_argument('-u', '--use-existing', action='store_true')
    args = arg_parser.parse_args()

    init_mix_network(args.num_servers, args.temp_folder, args.use_existing, args.server_public_host)

