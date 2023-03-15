import socket
from typing import List

from loguru import logger


def free_ports(num: int, cluster: bool = False, starting_port: int = -1) -> List:
    """Find free ports, for the number of nodes specified
    starting at the base port.
    """

    if starting_port != -1:
        return [i + starting_port for i in range(0, num)]

    ports = []
    while len(ports) != num:
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()

        # redis limitation
        if port >= 55535:
            continue

        s = socket.socket()
        try:
            s.bind(("", port + 10000))
        except OSError:  # port alread in use
            continue
        s.close()
        ports.append(port)
    return ports
