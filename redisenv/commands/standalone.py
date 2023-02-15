import sys

import click

from ..env import STANDALONE_TYPE, StandaloneHandler, _default_options
from ..composer import DockerComposeWrapper
from . import defaultenvname


def standalone():
    """create an environment with standalone redis nodes"""


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
    help="redis options, quoted",
    multiple=True,
    type=str,
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
):
    """create and start a new environment"""

    g = StandaloneHandler(ctx.obj.get("DESTDIR"), name)

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
    )
    if force:
        try:
            w.stop()
        except:
            pass
    g.start(sp, STANDALONE_TYPE)
