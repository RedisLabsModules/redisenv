import click
import sys
from ..env import _default_options, genenvspec, EnvironmentHandler
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
    help="Redis Version",
    default=_default_options["_version"],
    show_default=True,
)
@click.option(
    "--port",
    "-p",
    help="The listening port of the service, within the docker",
    default=_default_options["_port"],
    show_default=True,
)
@click.option(
    "--image",
    "-i",
    help="Set, to specify a source docker image",
    show_default=True,
    default=_default_options["_image"],
)
@click.option(
    "--mounts",
    "-M",
    help="Directories to mount into the dockers",
    multiple=True,
    type=(str, str),
)
@click.option("--conffile", "-f", help="Config file")
@click.option(
    "--ipv6",
    "-6",
    help="Set, to enable ipv6",
    is_flag=True,
    default=_default_options["_ipv6"],
)
@click.option(
    "--redisopts",
    "-o",
    help="Redis options, these must be quoted",
    multiple=True,
    type=str,
)
@click.pass_context
def create(
    ctx, name, force, nodes, version, port, image, mounts, conffile, ipv6, redisopts
):
    """Creates and starts a new environment"""
    sp = genenvspec(
        name,
        nodes,
        version,
        port,
        image,
        mounts,
        conffile,
        ipv6,
        redisopts,
        False,
    )
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    if force:
        try:
            g.stop(name)
        except:
            pass
    g.start(name, sp)
