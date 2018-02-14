from petlib.bn import Bn
from petlib.ec import EcPt 

from sphinxmix.SphinxParams import SphinxParams

from binascii import hexlify, unhexlify

import sys
import subprocess
import os
import os.path

from argparse import ArgumentParser

def public_key_to_str(public_key):
    return hexlify(public_key.export()).decode('utf-8')

def public_key_from_str(public_key_string, ecpt_group):
    public_key_byte_string = unhexlify(public_key_string.encode('utf-8'))
    return EcPt.from_binary(public_key_byte_string, ecpt_group)

def init_mix_network(num_servers, temp_folder, use_existing_config):
    params = SphinxParams()
    mix_nodes_filename = os.path.join(temp_folder, 'mix_nodes')
    client_config_filename = os.path.join(temp_folder, 'mix_network.csv')

    base_port = 8000
    server_ports = [str(base_port + i) for i in range(num_servers)]

    if not use_existing_config:
        private_keys = [params.group.gensecret() for i in range(num_servers)]

        mix_nodes = []
        for i in range(len(private_keys)):
            public_key = params.group.expon(params.group.g, private_keys[i])
            private_key_str = str(private_keys[i])
            public_key_str = public_key_to_str(public_key)
            mix_nodes.append((server_ports[i], public_key_str, private_key_str))

        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        output_file = open(mix_nodes_filename, 'w')

        for mix_node in mix_nodes:
            output_file.write(','.join(mix_node) + '\n')

        output_file.close()

        output_file = open(client_config_filename, 'w')

        for mix_node in mix_nodes:
            output_file.write(','.join(mix_node[:2]) + '\n')

        output_file.close()

    for port in server_ports:
        subprocess.Popen('python3 mix_server.py -p {} -f {} -t {}'.format(port, mix_nodes_filename, temp_folder), shell=True)
        print('Started server on:', port)

if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-n', '--num-servers', type=int, default=3)
    arg_parser.add_argument('-t', '--temp-folder', default='temp')
    arg_parser.add_argument('-u', '--use-existing', action='store_true')
    args = arg_parser.parse_args()

    init_mix_network(args.num_servers, args.temp_folder, args.use_existing)

