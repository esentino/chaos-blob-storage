"""
Feeder is responsible for handle communication between clients and nodes.
- Expose REST interface for client application
- by gossiper get information of all working nodes
- build information about blob part location and choose with node use to get blob data
- allow to store/remove/rename/duplicate blob files
"""
import tomli


def read_config(config_file: str):
    with open(file=config_file, mode="rb") as file_config:
        config_data = tomli.load(file_config)
        match config_data:
            case {
                "port": int(),
                "host": str(),
                "gossip": {"port": int(), "host": str()},
            }:
                pass
            case _:
                raise ValueError("Invalid config file")
    return config_data


def heartbeat(config):
    ...


if __name__ == "__main__":
    config = read_config("conf/feeder.toml")
