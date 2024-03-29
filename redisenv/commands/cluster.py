import sys

import click

from ..composer import DockerComposeWrapper
from ..env import ClusterHandler, _default_options
from ..util import free_ports
from . import defaultenvname


def cluster():
    """for creating an OSS redis cluster environment"""


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
@click.option(
    "--redisopts",
    "-o",
    help="redis options, quoted - passed to all containers",
    multiple=True,
    type=str,
)
@click.option(
    "--replicas",
    help="number of replicas in the cluster",
    default=_default_options["_cluster_replicas"],
    type=int,
)
@click.option(
    "--generate-only",
    help="set, to only generate the configurations, and not run them",
    is_flag=True,
    default=False,
)
@click.option(
    "--starting-port",
    help="If set to a value other than -1 (default), assign ports starting at the specified port",
    type=int,
    default=-1,
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
    redisopts,
    replicas,
    generate_only,
    starting_port,
):
    """create and start a new environment"""

    if nodes < 3:
        sys.stderr.write(
            "Exiting. At least 3 nodes are needed for this configuration.\n"
        )
        sys.exit(3)

    if replicas >= nodes:
        sys.stderr.write("There must be fewer replicas than nodes.\n")
        sys.exit(3)

    ports = free_ports(nodes, cluster=True, starting_port=starting_port)
    g = ClusterHandler(ctx.obj.get("DESTDIR"), name, generate_only=generate_only)
    w = DockerComposeWrapper(g)

    cfg = g.gen_config(ports, redisopts)

    sp = g.gen_spec(
        nodes,
        version,
        image,
        mounts,
        ports,
        replicas,
        starting_port,
    )

    if force:
        try:
            w.stop()
        except:
            pass
    g.start(cfg, sp)
