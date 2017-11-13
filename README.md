## Set-up

Install `pip` and `virtualenv`.

```
sudo apt-get install python3-pip
sudo pip3 install virtualenv
```

Install some native libraries required by the dependencies of this project.

```
sudo apt-get install libffi-dev
sudo apt-get install libssl-dev
```

Create a virtual environment and install dependencies.

```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

All commands below assume you are running them within the virtual environment (i.e. do `source venv/bin/activate` before running stuff below).

Create a `temp` directory where the code lives (this is where all the temporary files like logs and mix network configs are stored).

```
mkdir temp
```

Initialise the mix network. The init script takes two optional parameters - number of mix nodes (defaults to 10), and the output location of the mix network configuration file (defaults to `temp/mix_nodes`).

```
./init_mix.py [number of mix nodes] [mix network config output path]
```

This will spawn a number of `mix_server.py` instances. Each server's output can be seen in their log files, which follow the naming convention `temp/[server's port]`. The ports taken up by the servers start at 8000 and count upwards.

To send a message, the `mix_client.py` script can be used. The three required arguments are: path to the mix network config file created by `init_mix.py`, message destination, and message content. The fourth optional parameter specifies how many mix servers to randomly select from the network to route the message through (defaults to 2). Example:

```
./mix_client.py temp/mix_nodes Bob Hello 3
```

The above will randomly pick 3 nodes out the mix network and create a message to be routed through them. The final server on the path will output the message destination and content into its log file.

There is currently no "nice" way to close down the mix network, so at the moment the most convenient way is to do something along the lines of

```
pkill -f mix_server
```
