"""
Bringer is responsible for storing  parts blob file in directory
- contain information of blob files
- exchange information with other nodes
- send and receive parts blob file
- balance of number of parts blob file
"""
import socket
import struct
from typing import TypedDict

import tomli

from protocol import SIZE_COMMAND_FORMAT,NODE_NAME_FORMAT,MY_PORT_FORMAT
from protocol import COMMAND_FORMAT, Command


class GossipConfig(TypedDict):
    port: int
    host: str
    heartbeat: int


class BringerConfig(TypedDict):
    port: int
    host: str
    gossiper: GossipConfig
    name: str

def read_config(config_file: str) -> BringerConfig:
    with open(file=config_file, mode="rb") as file_config:
        config_data = tomli.load(file_config)
        print(config_data)
        match config_data:
            case {
                "port": int(),
                "host": str(),
                "name": str(),
                "gossiper": {"host": str(), "port": int(),  "heartbeat": int()},
            }:
                pass
            case _:
                raise ValueError("Invalid config file")
    return BringerConfig(
        port=config_data["port"],
        host=config_data["host"],
        name=config_data["name"],
        gossiper=GossipConfig(
            host=config_data["gossiper"]["host"],
            port=config_data["gossiper"]["port"],
            heartbeat=config_data["gossiper"]["heartbeat"],
        ),
    )


def get_the_gossips(config: BringerConfig):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((config["gossiper"]["host"], config["gossiper"]["port"]))
        s.sendall(struct.pack(COMMAND_FORMAT, Command.HELLO))
        response = s.recv(1024)
        command, = struct.unpack(COMMAND_FORMAT, response[:SIZE_COMMAND_FORMAT])
        if command != Command.HI:
            raise ValueError(f"Expect {Command.HI} get {command}")
        s.send(struct.pack(COMMAND_FORMAT, Command.I_AM_BRINGER))
        s.send(struct.pack(NODE_NAME_FORMAT,config['name'].encode('utf8')))
        response = s.recv(1024)
        command, = struct.unpack(COMMAND_FORMAT, response[:SIZE_COMMAND_FORMAT])
        if command != Command.COPY_THAT:
            raise ValueError(f"Expect {Command.COPY_THAT} get {command}")
        s.send(struct.pack(COMMAND_FORMAT, Command.MY_PORT))
        s.send(struct.pack(MY_PORT_FORMAT, config["port"]))
        response = s.recv(1024)
        command, = struct.unpack(COMMAND_FORMAT, response[:SIZE_COMMAND_FORMAT])
        if command != Command.COPY_THAT:
            raise ValueError(f"Expect {Command.COPY_THAT} get {command}")

if __name__ == "__main__":
    config = read_config("conf/bringer.toml")
    get_the_gossips(config)
