import sys

import click

from ..composer import DockerComposeWrapper
from ..env import REPLICAOF_TYPE, ReplicaHandler, _default_options
from . import defaultenvname


def replica():
    """creating an environment containing redis replicas"""


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
    help="Number of nodes",
    default=2,
    type=int,
    show_default=True,
)
@click.option(
    "--version",
    "-v",
    help="redis version (i.e docker tag)",
    default=_default_options["_version"],
    show_default=True,
)
@click.option(
    "--image",
    "-i",
    help="Set, to specify a source docker image (without tag)",
    show_default=True,
    default=_default_options["_image"],
)
@click.option(
    "--mounts",
    "-M",
    help="directories to mount into all dockers (local remote)",
    multiple=True,
    type=(str, str),
)
@click.option("--conffile", "-f", help="Config file")
@click.option(
    "--ipv6",
    "-6",
    help="enable ipv6",
    is_flag=True,
    default=_default_options["_ipv6"],
)
@click.option(
    "--redisopts",
    "-o",
    help="redis options, quoted - passed to all containers",
    multiple=True,
    type=str,
)
@click.option(
    "--replicaof",
    type=int,
    default=-1,
    help="If set nodes replicate the specified port, if not first node is replicated.",
)
@click.option(
    "--docker-ip",
    type=str,
    default="172.0.0.1",
    help="Set, to override the  docker ip (mostly used with the replicaof options)",
)
@click.pass_context
def create(
    ctx,
    name,
    force,
    nodes,
    version,
    image,
    mounts,
    conffile,
    ipv6,
    redisopts,
    replicaof,
    docker_ip,
):
    """create and start a new environment"""
    if replicaof == -1:
        if nodes < 2:
            sys.stderr.write("To configure replicas, at least two nodes are needed.\n")
            sys.exit(3)

    g = ReplicaHandler(ctx.obj.get("DESTDIR"), name)
    w = DockerComposeWrapper(g)
    sp = g.gen_spec(
        name,
        nodes,
        version,
        image,
        mounts,
        conffile,
        ipv6,
        redisopts,
        replicaof,
        docker_ip,
    )

    if force:
        try:
            w.stop()
        except:
            pass
    g.start(sp, REPLICAOF_TYPE)
