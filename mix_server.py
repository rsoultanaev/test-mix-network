#!venv/bin/python3

from sphinxmix.SphinxParams import SphinxParams
from sphinxmix.SphinxClient import pack_message, unpack_message
from sphinxmix.SphinxNode import sphinx_process
from sphinxmix.SphinxClient import PFdecode, Relay_flag, Dest_flag, Surb_flag, receive_forward

from datetime import datetime

from petlib.bn import Bn

from uuid import UUID
from binascii import hexlify

import sys
import asyncio
import os
import os.path

from base64 import b64encode

from init_mix import public_key_from_str

params = SphinxParams()
param_dict = { (params.max_len, params.m): params }
temp_folder = 'temp'

my_port = int(sys.argv[1])
port_to_public_key = dict()

if len(sys.argv) == 3:
    # Use file as source of mix network info
    mix_network_filename = sys.argv[2]
    mix_network_file = open(mix_network_filename)

    for line in mix_network_file.readlines():
        split_line = line[:-1].split(',')

        port = int(split_line[0])

        if port == my_port:
            my_public_key = public_key_from_str(split_line[1], params.group.G)
            my_private_key = Bn.from_decimal(split_line[2])
        else:
            public_key = public_key_from_str(split_line[1], params.group.G)
            port_to_public_key[port] = public_key

    mix_network_file.close()
else:
    # Use command line params as source of mix network info
    my_port = int(sys.argv[1])
    my_private_key = Bn.from_decimal(sys.argv[2])
    my_public_key = public_key_from_str(sys.argv[3], params.group.G)

    for i in range(4, len(sys.argv), 2):
        port = int(sys.argv[i])
        public_key = public_key_from_str(sys.argv[i + 1], params.group.G)
        port_to_public_key[port] = public_key

if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

log_filename = os.path.join(temp_folder, str(my_port))
log_file = open(log_filename, 'a')

async def process_message(reader, writer):
    data = await reader.read()

    _, (received_header, received_delta) = unpack_message(param_dict, data)
    (tag, info, (header, delta)) = sphinx_process(params, my_private_key, received_header, received_delta)
    routing = PFdecode(params, info)

    if routing[0] == Relay_flag:
        next_port = routing[1]
        log_file.write('{:%Y_%m_%d_%H_%M_%S} -- Relaying to: {}\n'.format(datetime.now(), next_port))
        log_file.flush()

        _, next_writer = await asyncio.open_connection('127.0.0.1', next_port)
        next_message = pack_message(params, (header, delta))

        next_writer.write(next_message)
        await next_writer.drain()

        next_writer.close()
    elif routing[0] == Dest_flag:
        final_dest, final_message = receive_forward(params, delta)

        message_id = str(UUID(bytes=final_message[:16]))
        packets_in_message = int.from_bytes(final_message[16:20], byteorder='big')
        sequence_number = int.from_bytes(final_message[20:24], byteorder='big')

        log_file.write('{:%Y_%m_%d_%H_%M_%S}\n'.format(datetime.now()))
        log_file.write('Received packet for: {}\n'.format(final_dest.decode()))
        log_file.write('Message ID:          {}\n'.format(message_id))
        log_file.write('Packets in message:  {}\n'.format(packets_in_message))
        log_file.write('Sequence number:     {}\n'.format(sequence_number))
        log_file.flush()

        encoded_packet = b64encode(final_message)
        email_subject = bytes('Subject: {}, {}, {}\r\n'.format(message_id, packets_in_message, sequence_number), 'utf-8')
        _, email_writer = await asyncio.open_connection('127.0.0.1', 25)

        email_msg =  b'EHLO localhost\r\n'
        email_msg += b'mail from: mixserver' + bytes(str(my_port), 'utf-8') + b'@sphinx.com\r\n'
        email_msg += b'rcpt to: ' + bytes(final_dest) + b'\r\n'
        email_msg += b'data\r\n'
        email_msg += email_subject
        #email_msg += b'Subject: Sphinx packet\r\n'
        email_msg += encoded_packet
        email_msg += b'\r\n.\r\n'
        email_msg += b'QUIT\r\n'

        email_writer.write(email_msg)
        await email_writer.drain()
        email_writer.close()

    writer.close()

loop = asyncio.get_event_loop()
coro = asyncio.start_server(process_message, '127.0.0.1', my_port, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
log_file.write('{:%Y_%m_%d_%H_%M_%S} -- Serving on {}\n'.format(datetime.now(), server.sockets[0].getsockname()))
log_file.flush()
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

log_file.close()
