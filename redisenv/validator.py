import json
import subprocess
import sys

import docker
import semver
from loguru import logger


def checkenv():
    """Checks prerequisites"""
    _docker()
    _compose()
    _ipv6()


def _ipv6():
    with open("/etc/docker/daemon.json") as fp:
        d = json.load(fp)
        if d.get("ipv6", False) != True:
            logger.critical("docker must be configured to allow for ipv6")
            logger.info("See https://docs.docker.com/config/daemon/ipv6/")
            sys.exit(3)


def _docker():
    e = docker.from_env()
    try:
        e.ping()
    except docker.errors.DockerException:
        logger.critical("unable to connect to docker service, exiting")
        sys.exit(3)


def _compose():
    try:
        x = subprocess.Popen(
            ["docker-compose", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        version = x.stdout.read().decode().split()[-1]
    except IndexError:
        logger.critical(
            "docker compose failed to return a version, you probably need something newer"
        )
    except:
        logger.critical("no docker-compose found")
        sys.exit(3)

    try:
        if semver.compare("2.0.2", version) == 1:
            logger.critical("docker-comose >= 2.0.2 is required")
            logger.info("get it here: https://github.com/docker/compose")
            sys.exit(3)

    except ValueError:
        logger.critical("docker-comose >= 2.0.2 is required")
        logger.info("get it here: https://github.com/docker/compose")
        sys.exit(3)
