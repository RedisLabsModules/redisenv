import os
import shutil

import click
from loguru import logger

from ..env import EnvironmentHandler

defaultenvname = "myenv"


@click.group()
@click.option("--debug", "-x", help="Enable debug output", default=False, is_flag=True)
@click.option("--quiet", "-q", help="Quiet all outputs", default=False, is_flag=True)
@click.option(
    "--dest",
    "-d",
    help="Directory for environment files",
    default=os.path.join(os.getcwd(), "redisenv.envs"),
    show_default=True,
)
@click.option(
    "--templates",
    "-t",
    help="Directory for environment templates",
    default=os.path.join(os.getcwd(), "redisenv.templates"),
    show_default=True,
)
@click.pass_context
def cli(ctx, debug, quiet, dest, templates):
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    ctx.obj["DESTDIR"] = dest
    ctx.obj["TEMPLATEDIR"] = templates
    if debug:
        logger.level("DEBUG")
    if quiet:
        logger.level("CRITICAL")


@cli.command()
@click.option(
    "--name",
    help="environment name",
    default=defaultenvname,
    show_default=True,
)
@click.pass_context
def destroy(ctx, name):
    """destroy an environment"""
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.stop(name)
    os.unlink(g._envfile(name))
    tree = os.path.join(g.envdir, name)
    if os.path.isdir(tree):
        shutil.rmtree(tree)


@cli.command()
@click.option(
    "--name",
    help="environment name",
    default=defaultenvname,
    show_default=True,
)
@click.pass_context
def pause(ctx, name):
    """pause an environment"""
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.pause(name)


@cli.command()
@click.option(
    "--name",
    help="environment name",
    default=defaultenvname,
    show_default=True,
)
@click.pass_context
def unpause(ctx, name):
    """unpause an environment"""
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.unpause(name)


@cli.command()
@click.option(
    "--name",
    help="environment name",
    default=defaultenvname,
    show_default=True,
)
@click.pass_context
def restart(ctx, name):
    """restart an environment"""
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.restart(name)


@cli.command()
@click.option(
    "--generated",
    "-g",
    help="set, to list generated environments (instead of templates)",
    is_flag=True,
)
@click.pass_context
def listenvs(ctx, generated):
    """list environments"""
    if generated:
        envdir = ctx.obj.get("DESTDIR")
    else:
        envdir = ctx.obj.get("TEMPLATEDIR")
    g = EnvironmentHandler(envdir)
    g.listenvs()


@cli.command()
@click.option(
    "--name",
    help="environment name",
    default=defaultenvname,
    show_default=True,
)
@click.pass_context
def ports(ctx, name):
    """List the ports generated for an environment"""
    g = EnvironmentHandler(ctx.obj.get("DESTDIR"))
    g.listports(name)
