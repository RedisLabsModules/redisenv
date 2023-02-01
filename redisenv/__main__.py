import click
import os
import sys
from loguru import logger

from .env import _default_options, genenvspec, EnvironmentHandler
from .validator import checkenv


@click.group()
@click.option("--name", help="Environment name")
@click.option("--debug", "-x", help="Enable debug output", default=False, is_flag=True)
@click.option(
    "--destdir",
    "-d",
    help="Directory for environment files",
    default=os.path.join(os.getcwd(), ".redisenvs"),
    show_default=True,
)
@click.pass_context
def cli(ctx, name, debug, destdir):
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    ctx.obj["NAME"] = name
    ctx.obj["DESTDIR"] = destdir

    if debug:
        logger.level("DEBUG")
    checkenv()


@cli.command()
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
# @click.option("--enterprise", "-e", is_flag=True, help="Set, for redis enterprise", default=False)
@click.pass_context
# def start(ctx, force, nodes, version, conffile, ipv6, port, module, mounts):
def create(ctx, force, nodes, version, port, image, mounts, conffile, ipv6, redisopts):
    """Creates and starts a new environment"""
    if ctx.obj.get("NAME") is None:
        sys.stderr.write("--name is required\n.")
        sys.exit(3)

    sp = genenvspec(
        ctx.obj.get("NAME"),
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
            g.stop(ctx.obj.get("NAME"))
        except:
            pass
    g.start(ctx.obj.get("NAME"), sp)


def load(ctx):
    """Load and stat the named environment"""
    if ctx.obj.get("NAME") is None:
        sys.stderr.write("--name is required\n.")
        sys.exit(3)
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.start(ctx.obj.get("NAME"))


@cli.command()
@click.pass_context
def destroy(ctx):
    """Stop the running environment"""
    if ctx.obj.get("NAME") is None:
        sys.stderr.write("--name is required\n.")
        sys.exit(3)
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.stop(ctx.obj.get("NAME"))


@click.command()
@click.option(
    "--ports", "-p", help="Set, to outputs ports as a json string", is_flag=True
)
@click.pass_context
def list(ctx, ports):
    """List the environments"""
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))

    if ports:
        if ctx.obj.get("NAME") is None:
            sys.stderr.write("--name is required\n.")
            sys.exit(3)
        g.listports(name=ctx.obj.get("NAME"), output=True)
    else:
        g.listenvs()


@cli.command()
@click.pass_context
def pause(ctx):
    """Pause the named environment"""
    if ctx.obj.get("NAME") is None:
        sys.stderr.write("--name is required\n.")
        sys.exit(3)
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.pause(ctx.obj.get("NAME"))


@cli.command()
@click.pass_context
def unpause(ctx):
    """Unpause the named environment"""
    if ctx.obj.get("NAME") is None:
        sys.stderr.write("--name is required\n.")
        sys.exit(3)
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.unpause(ctx.obj.get("NAME"))


@cli.command()
@click.pass_context
def restart(ctx):
    """Unpause the named environment"""
    if ctx.obj.get("NAME") is None:
        sys.stderr.write("--name is required\n.")
        sys.exit(3)
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.restart(ctx.obj.get("NAME"))


cli.add_command(create)
cli.add_command(destroy)
cli.add_command(pause)
cli.add_command(unpause)
cli.add_command(list)

if __name__ == "__main__":
    cli()
