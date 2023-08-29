"""
Gossiper app hold information about all connected node and is responsible for exchange information
on changes in changes of nodes.
- Each node send heartbeat information to gossiper (I'm still alive and kicking)
- Gossiper distribute that information to rest of node of changes
- Gossiper remove node from list if node don't response
"""
import selectors
import socket
import struct
import types
from selectors import SelectorKey
from typing import TypedDict

import tomli
from protocol import (
    COMMAND_FORMAT,
    MY_IP_FORMAT,
    MY_PORT_FORMAT,
    NODE_NAME_FORMAT,
    SIZE_COMMAND_FORMAT,
    SIZE_MY_IP_FORMAT,
    SIZE_MY_PORT,
    SIZE_NODE_NAME_FORMAT,
    Command,
)


class GossipNodeConfig(TypedDict):
    heartbeat: int
    gossip_timeout: int


class GossiperConfig(TypedDict):
    port: int
    host: str
    node: GossipNodeConfig


def read_config(config_file: str) -> GossiperConfig:
    with open(file=config_file, mode="rb") as file_config:
        config_data = tomli.load(file_config)
        match config_data:
            case {
                "port": int(),
                "host": str(),
                "node": {"heartbeat": int(), "gossip_timeout": int()},
            }:
                pass
            case _:
                raise ValueError("Invalid config file")
    return GossiperConfig(
        port=config_data["port"],
        host=config_data["host"],
        node=GossipNodeConfig(
            heartbeat=config_data["node"]["heartbeat"],
            gossip_timeout=config_data["node"]["gossip_timeout"],
        ),
    )


def accept_connection(socket, selector):
    connection, address = socket.accept()
    print(f"Set ears to {address}")
    connection.setblocking(False)
    data = types.SimpleNamespace(
        addr=address,
        inb=b"",
        outb=b"",
        node_name=None,
        node_port=None,
        node_host=None,
        its_end=False,
    )

    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(connection, events, data=data)


def handle_incoming_data(data):
    if len(data.inb) < 1:
        return
    command = get_method(data)
    match command:
        case Command.HELLO:
            data.outb += struct.pack(COMMAND_FORMAT, Command.HI)
            data.inb = data.inb[SIZE_COMMAND_FORMAT:]
        case Command.I_AM_BRINGER:
            if len(data.inb) >= SIZE_COMMAND_FORMAT + SIZE_NODE_NAME_FORMAT:
                node_name = get_node_name(data)
                data.inb = data.inb[SIZE_COMMAND_FORMAT:]
                data.outb += struct.pack(COMMAND_FORMAT, Command.COPY_THAT)
                data.inb = data.inb[SIZE_NODE_NAME_FORMAT:]
                data.node_name = node_name
        case Command.MY_PORT:
            if len(data.inb) >= SIZE_COMMAND_FORMAT + SIZE_MY_PORT:
                data.inb = data.inb[SIZE_COMMAND_FORMAT:]
                (port,) = struct.unpack(MY_PORT_FORMAT, data.inb[:SIZE_MY_PORT])
                data.inb = data.inb[SIZE_MY_PORT:]
                data.node_port = port
                data.outb += struct.pack(COMMAND_FORMAT, Command.COPY_THAT)
        case Command.MY_IP:
            if len(data.inb) >= SIZE_COMMAND_FORMAT + SIZE_MY_IP_FORMAT:
                data.inb = data.inb[SIZE_COMMAND_FORMAT:]
                (int_ip,) = struct.unpack(MY_IP_FORMAT, data.inb[:SIZE_MY_IP_FORMAT])
                data.inb = data.inb[SIZE_MY_IP_FORMAT:]
                data.node_ip = int_ip
                data.outb += struct.pack(COMMAND_FORMAT, Command.COPY_THAT)


def get_method(data):
    command_data = data.inb[:SIZE_COMMAND_FORMAT]
    (command,) = struct.unpack(COMMAND_FORMAT, command_data)
    return command


def get_node_name(data):
    string_data = data.inb[:SIZE_NODE_NAME_FORMAT]
    (node_name,) = struct.unpack(NODE_NAME_FORMAT, string_data)
    return node_name


def service_connection(key: SelectorKey, mask: int, selector):
    """
    Flow of communication
    - Feeder/bringer Start Communication send what want to do
    - Gossiper return information.
    """
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.inb += recv_data
            print(data.inb)
        handle_incoming_data(data)
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
        if not data.outb and data.its_end:
            print(f"End of gossiping with {data.addr}")
            selector.unregister(sock)
            sock.close()


def gather_gossip(config: GossiperConfig):
    sel = selectors.DefaultSelector()
    listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = config["host"]
    port = config["port"]
    address = (host, port)
    listening_sock.bind(address)
    listening_sock.listen()
    print(f"Gossiper set ears on {address}")
    listening_sock.setblocking(False)
    sel.register(listening_sock, selectors.EVENT_READ, data=None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_connection(key.fileobj, sel)
                else:
                    service_connection(key, mask, sel)
    except KeyboardInterrupt:
        print("Hit by keyboard, hurt a lot")
    finally:
        sel.close()


if __name__ == "__main__":
    config = read_config("conf/gossiper.toml")
    gather_gossip(config)
