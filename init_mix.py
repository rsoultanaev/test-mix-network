#!venv/bin/python3

from petlib.bn import Bn
from petlib.ec import EcPt 

from sphinxmix.SphinxParams import SphinxParams

from binascii import hexlify, unhexlify

import sys
import subprocess
import os
import os.path

params = SphinxParams()
temp_folder = 'temp'

def public_key_to_str(public_key):
    return hexlify(public_key.export()).decode('utf-8')

def public_key_from_str(public_key_string, ecpt_group):
    public_key_byte_string = unhexlify(public_key_string.encode('utf-8'))
    return EcPt.from_binary(public_key_byte_string, ecpt_group)

def init_mix_network(num_servers=10, output_filename='mix_nodes'):
    base_port = 8000
    server_ports = [str(base_port + i) for i in range(num_servers)]
    private_keys = [params.group.gensecret() for i in range(num_servers)]

    mix_nodes = []
    for i in range(len(private_keys)):
        public_key = params.group.expon(params.group.g, private_keys[i])
        private_key_str = str(private_keys[i])
        public_key_str = public_key_to_str(public_key)
        mix_nodes.append((server_ports[i], public_key_str, private_key_str))

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    output_filename = os.path.join(temp_folder, output_filename)
    output_file = open(output_filename, 'w')

    for mix_node in mix_nodes:
        output_file.write(','.join(mix_node) + '\n')

    output_file.close()

    for port in server_ports:
        subprocess.Popen('./mix_server.py {} {}'.format(port, output_filename), shell=True)
        print('Started server on:', port)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        init_mix_network()
    elif len(sys.argv) == 2:
        init_mix_network(int(sys.argv[1]))
    else:
        init_mix_network(int(sys.argv[1]), sys.argv[2])

