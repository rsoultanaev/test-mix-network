from sphinxmix.SphinxClient import *
from sphinxmix.SphinxParams import SphinxParams
from sphinxmix.SphinxNode import sphinx_process

from petlib.bn import Bn

from base64 import b64encode

import sys
import subprocess


def run_client_under_test(client_command, dest, message, use_nodes, node_keys):
    dest_encoded = b64encode(dest).decode()
    message_encoded = b64encode(message_encoded).decode()

    node_key_pairs = []
    for i in len(use_nodes):
        node_key_pairs.append(str(use_nodes[i]) + ":" + b64encode(node_keys[i].export()).decode())

    run_command = [client_command, dest_encoded, message_encoded]
    for node_key_pair in node_key_pairs:
        run_command.append(node_key_pair)

    return subprocess.run(run_command, stdout=subprocess.PIPE)


def test_create_forward_message_creation(client_command, num_mix_nodes=10, num_path_nodes=5):
    params = SphinxParams()
    
    pkiPriv = {}
    pkiPub = {}

    for i in range(num_mix_nodes):
        nid = pack("b", i)
        x = params.group.gensecret()
        y = params.group.expon(params.group.g, x)
        pkiPriv[nid] = pki_entry(nid, x, y)
        pkiPub[nid] = pki_entry(nid, None, y)

    use_nodes = rand_subset(pkiPub.keys(), num_path_nodes)
    nodes_routing = list(map(Nenc, use_nodes))
    node_keys = [pkiPub[n].y for n in use_nodes]

    dest = b"bob"
    message = b"this is a test"

    bin_message = run_client_under_test(client_command, dest, message, use_nodes, node_keys)

    param_dict = { (params.max_len, params.m): params }
    _, (header, delta) = unpack_message(param_dict, bin_message)

    x = pkiPriv[use_nodes[0]].x

    while True:
        ret = sphinx_process(params, x, header, delta)
        (tag, B, (header, delta)) = ret
        routing = PFdecode(params, B)

        if routing[0] == Relay_flag:
            addr = routing[1]
            x = pkiPriv[addr].x 
        elif routing[0] == Dest_flag:
            dec_dest, dec_msg = receive_forward(params, delta)

            if dec_dest == dest and dec_msg == message:
                print("Success")
            else:
                print("Failure")

            break
        else:
            print("Failure")
            break


if __name__ == "__main__":
    test_create_forward_message_creation(int(sys.argv[1])):

