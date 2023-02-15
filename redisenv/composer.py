from loguru import logger
from typing import List
import subprocess


class DockerComposeWrapper:
    """A wrapper around docker compose"""

    def __init__(self, environment):
        self._env = environment

    def _build(self, *args) -> List:
        return ["docker-compose", "-f", self._env.envfile, *args]

    def pause(self):
        """pause the environment"""
        cmd = self._build("pause")

        logger.info(f"Pausing environment {self._env.envfile}")

        try:
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to pause the environment {self._env.envname}")
            raise

    def unpause(self):
        """unpause the paused environment"""
        cmd = self._build("unpause")

        logger.info(f"Unpausing environment {self._env.envfile}")

        try:
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to unpause the environment {self._env.envname}")
            raise

    def restart(self):
        """restart the named environment"""
        cmd = self._build("restart")

        logger.info(f"Restarting environment {self._env.envfile}")

        try:
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to restart the environment {self._env.envname}")
            raise

    def stop(self):
        """stop the named environment"""
        cmd = self._build("rm", "-s", "-f")

        logger.info(f"Stopping environment {self._env.envfile}")

        try:
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to stop the environment {self._env.envname}")
            raise
