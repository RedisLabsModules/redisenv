import sys

import click

from ..composer import DockerComposeWrapper
from ..env import SentinelHandler, _default_options
from ..util import free_ports
from . import defaultenvname


def sentinel():
    """create a redis-sentinel environment"""


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
    default=4,
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
@click.option("--redisconf", "-c", help="redis instance configuration file")
@click.option(
    "--user",
    "-u",
    help="Set, to specify a sentinel user",
)
@click.option(
    "--password",
    "-p",
    help="Set, to specify a sentinel password",
)
@click.option(
    "--sentinelopts",
    "-s",
    help="sentinel options, quoted. If these are specified they fully override the defaults",
    multiple=True,
    type=str,
)
@click.option(
    "--redisopts",
    "-o",
    help="redis options, quoted. These are the configuration options for the Redis (not sentinel) nodes",
    multiple=True,
    type=str,
)
@click.option(
    "--docker-ip",
    type=str,
    default="172.0.0.1",
    help="Set, to override the docker ip (i.e if you want to use an existing redis)",
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
    redisconf,
    user,
    password,
    sentinelopts,
    redisopts,
    docker_ip,
    generate_only,
    starting_port,
):
    """create and start a new environment"""

    if nodes < 4:
        sys.stderr.write(
            "Exiting. At least 4 nodes are needed for this configuration.\n"
        )
        sys.exit(3)

    ports = free_ports(nodes, starting_port=starting_port)
    g = SentinelHandler(ctx.obj.get("DESTDIR"), name, generate_only=generate_only)
    w = DockerComposeWrapper(g)

    cfg = g.gen_config(
        ports,
        user,
        password,
        sentinelopts,
        docker_ip,
    )

    sp = g.gen_spec(
        nodes=nodes,
        version=version,
        image=image,
        mounts=mounts,
        redisconf=redisconf,
        redisopts=redisopts,
        ports=ports,
        starting_port=starting_port,
    )

    if force:
        try:
            w.stop()
        except:
            pass
    g.start(cfg, sp)
