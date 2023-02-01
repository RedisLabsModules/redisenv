from typing import List
from loguru import logger
import socket


def free_ports(num: int) -> List:
    """Find free ports, for the number of nodes specified
    starting at the base port.
    """
    ports = []
    for i in range(num):
        s = socket.socket()
        s.bind(("", 0))
        ports.append(s.getsockname()[1])
        s.close()
    return ports
