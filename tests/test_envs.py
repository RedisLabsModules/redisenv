import importlib
import os
import subprocess
import sys
import time

import docker
import pytest
from click.testing import CliRunner

_here = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(_here, "../"))

environments = [
    "standalone",
    "replica",
    "sentinel",
    "cluster",
]


@pytest.mark.parametrize(
    "env_type",
    argvalues=environments,
)
def test_help_text(env_type):
    g = importlib.import_module(f"redisenv.commands.{env_type}")
    r = CliRunner()
    result = r.invoke(g.create, ["--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "env_type",
    argvalues=environments,
)
def test_start_restart_destroy(env_type):
    cmd = [sys.executable, "-m", "redisenv", env_type, "create"]
    subprocess.run(
        cmd, check=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # give the containers time to start and settle
    time.sleep(1)

    cmd = [sys.executable, "-m", "redisenv", "restart"]
    subprocess.run(
        cmd, check=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    cmd = [sys.executable, "-m", "redisenv", "destroy"]
    subprocess.run(
        cmd, check=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def test_pause_unpause():
    env_type = "standalone"
    cmds = []
    cmds.append([sys.executable, "-m", "redisenv", env_type, "create"])
    cmds.append([sys.executable, "-m", "redisenv", "pause"])
    cmds.append([sys.executable, "-m", "redisenv", "unpause"])
    cmds.append([sys.executable, "-m", "redisenv", "destroy"])

    for c in cmds:

        subprocess.run(
            c, check=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
