import click
import sys
from ..env import EnvironmentHandler, STANDALONE_TYPE
from ..envhelpers import _default_options, genstandalonespec
from . import defaultenvname


def standalone():
    """for creating an environment based on standalone redis"""


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
    default=_default_options["_nodes"],
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
    help="redis options, quoted",
    multiple=True,
    type=str,
)
@click.option(
    "--docker-ip",
    type=str,
    default="172.0.0.1",
    help="Set, to override the  docker ip (i.e if you want to use an existing redis)",
)
@click.pass_context
def create(ctx, name, force, nodes, version, image, mounts, conffile, ipv6, redisopts, docker_ip):
    """create and start a new environment"""
    sp = genstandalonespec(
        name,
        nodes,
        version,
        image,
        mounts,
        conffile,
        ipv6,
        redisopts,
        docker_ip,
    )
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    if force:
        try:
            g.stop(name)
        except:
            pass
    g.start(name, sp, STANDALONE_TYPE)
