# Sphinx-based mix network for testing purposes

## Set-up

Install `pip3`.

```
sudo apt-get install python3-pip
```

Install some native libraries required by the dependencies of this project.

```
sudo apt-get install libffi-dev
sudo apt-get install libssl-dev
```

Install dependencies.

```
pip3 install -r requirements.txt
```

## Usage

Both `init_mix.py` and `mix_server.py` will put temporary files like logs and generated mix network configs into a specified temporary folder (`temp` by default). The folder is created automatically if it doesn't already exist.

Initialise the mix network. The init script takes three optional parameters - number of mix nodes (defaults to 3), name of the temporary folder (defaults to `temp`), and whether to use an existing config (will look for it in the temporary folder).

```
python3 init_mix.py [-n number of mix nodes] [-t temporary folder] [-u]
```

This will spawn a number of `mix_server.py` instances. Each server's output can be seen in their log files, which follow the naming convention `temp/[server's port]`. The ports taken up by the servers start at 8000 and count upwards.

To send a message, the `mix_client.py` script can be used. The arguments are: path to the mix network config file created by `init_mix.py`, message destination, and message content. The fourth optional parameter specifies how many mix servers to randomly select from the network to route the message through (defaults to 2). Example:

```
python3 mix_client.py -f temp/mix_nodes -d bob@somemail.com -m hello -r 3
```

The above will randomly pick 3 nodes out the mix network and create a message to be routed through them. The final server on the path will output the message destination and content into its log file.

There is currently no "nice" way to close down the mix network, so at the moment the most convenient way is to do something along the lines of

```
pkill -f mix_server
```

# Conformance test

For the conformance test against the Python Sphinx library, see the `conformance_test` directory for the test and manual.
