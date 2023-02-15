import socket
import sys

import click
from loguru import logger

from ..composer import DockerComposeWrapper
from ..env import ENTERPRISE_CLUSTER_TYPE, EnterpriseClusterHandler, _default_options
from ..util import free_ports
from . import defaultenvname


def enterprise():
    """for creating redis enterprise clusters"""


@click.command()
@click.option(
    "--name",
    help="environment name",
    default=defaultenvname,
    show_default=True,
)
@click.option(
    "--force",
    help="Set, to force , if the environment exists",
    default=False,
    show_default=True,
    is_flag=True,
)
@click.option(
    "--nodes",
    "-n",
    help="Number of nodes, first node will be a standard redis node",
    default=3,
    type=int,
    show_default=True,
)
@click.option(
    "--databases",
    "-d",
    help="Number of databases - this will pre allocate ports",
    default=3,
    type=int,
    show_default=True,
)
@click.option(
    "--version",
    "-v",
    help="redis version (i.e docker tag)",
    default="latest",
    show_default=True,
)
@click.option(
    "--mounts",
    "-M",
    help="directories to mount into all dockers (local remote)",
    multiple=True,
    type=(str, str),
)
@click.option(
    "--username",
    "-u",
    help="redis cluster username",
    default="test@redis.com",
    show_default=True,
)
@click.option(
    "--password",
    "-p",
    help="redis cluster password",
    default="redis123",
    show_default=True,
)
@click.pass_context
def create(
    ctx,
    name,
    force,
    nodes,
    databases,
    version,
    mounts,
    username,
    password,
):
    """create and start a redis enterprise cluster"""

    if nodes < 3:
        sys.stderr.write(
            "Exiting. At least 3 nodes are needed for this configuration.\n"
        )
        sys.exit(3)

    g = EnterpriseClusterHandler(ctx.obj.get("DESTDIR"), name)
    w = DockerComposeWrapper(g)

    ports = [8443, 9443]
    for p in ports:
        s = socket.socket()
        try:
            s.bind(("", p))
        except OSError:
            logger.critical(f"At least one of port {ports} is not free. Exiting.")
            sys.exit(3)
        s.close()

    ports = free_ports(databases)

    sp = g.gen_spec(nodes, version, ports, mounts)
    g.credentials(username, password)

    if force:
        try:
            w.stop()
        except:
            pass
    print(sp)
    g.start(sp, ENTERPRISE_CLUSTER_TYPE)
