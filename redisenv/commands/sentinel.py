import click
import sys
from ..env import EnvironmentHandler
from ..envhelpers import _default_options, gensentinelspec, gensentinelconf
from . import defaultenvname


def sentinel():
    """for creating a redis-sentinel environment"""

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
    help="directories to mount into the dockers (local remote)",
    multiple=True,
    type=(str, str),
)
@click.option("--redisconf", "-c", help="redis instance configuration file")
@click.option("--templatefile", "-t", help="sentinel base template")
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
    help="redis options, quoted - thse are added to the generated, sentinel.conf",
    multiple=True,
    type=str,
)
@click.option(
    "--redisopts",
    "-o",
    help="redis options, quoted - thse are added to the generated, sentinel.conf",
    multiple=True,
    type=str,
)
@click.pass_context
def create(
    ctx, name, force, nodes, version, image, mounts, redisconf, templatefile, user, password, sentinelopts, redisopts
):
    """create and start a new environment"""
    
    if nodes < 4:
        sys.stderr.write("Exiting. At least 4 nodes are needed for this configuration.\n")
        sys.exit(3)
        
    from ..util import free_ports
    ports = free_ports(nodes)
    
    sp = gensentinelspec(
        name,
        nodes,
        version,
        image,
        mounts,
        redisconf,
        redisopts,
        ports,
    )
    
    if templatefile != "":
        cfg = gensentinelconf(
            ports,
            user,
            password,
            sentinelopts,
            templatefile,
        )
    print(cfg)
    sys.exit(3)
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    if force:
        try:
            g.stop(name)
        except:
            pass
    g.start(name, sp)
