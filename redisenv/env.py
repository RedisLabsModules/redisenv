import jinja2
import yaml
import os
from loguru import logger
from typing import Dict, List, Optional
import json
import subprocess


class EnvironmentHandler:
    """Environment"""

    def __init__(self, destdir: str, disable_logging=False):
        self._ENVDIR = destdir
        if disable_logging:
            logger.disable("redisenv")

    def listenvs(self):
        """List the environments"""

        if not os.path.isdir(self.envdir):
            logger.info(f"No environments found in {self.envdir}")
            return
        for x in os.listdir(self.envdir):
            logger.info(x)

    def listports(self, name, output=True):
        """Output the ports (as json) for the specified environment
        Set output to False, if using this in a library"""
        d = yaml.safe_load(open(self._getenv(name)))
        ports = {}
        for k, i in d.get("services").items():
            port = int(i["ports"][0].split(":")[0])
            ports[k] = {"port": port, "connstr": f"redis://localhost:{port}"}

        if output:
            print(json.dumps(ports))
        return ports

    def _getenv(self, name):
        e = self._envfile(name)
        if not os.path.isfile(e):
            logger.critical(f"{name} does not exist")
            return
        return e

    @property
    def envdir(self):
        return self._ENVDIR

    def _envfile(self, name: str):
        return os.path.join(self.envdir, f"{name}.yml")

    def _generate(self, name: str, config: Dict, redistype: str):
        """Generate the environment configuration"""
        if not os.path.isdir(self.envdir):
            os.makedirs(self.envdir)

        destfile = self._envfile(name)
        here = os.path.join(os.path.dirname(__file__), "templates")

        # add the environment here
        tmpl = jinja2.FileSystemLoader(searchpath=here)
        tenv = jinja2.Environment(loader=tmpl)
        if redistype == "standalone":
            templatefile = "standalone.tmpl"
        elif redistype == "replicaof":
            templatefile = "replicaof.tmpl"
        tmpl = tenv.get_template(templatefile)
        with open(destfile, "w+") as fp:
            logger.debug(f"Writing {destfile}")
            fp.write(tmpl.render(config))

    def start(self, name: str, config: Optional[Dict], redistype: str="standalone"):
        """Start the environment"""
        if config:
            logger.info(f"Generating environment {name}")
            self._generate(name, config, redistype)
        cmd = ["docker-compose", "-f", self._envfile(name), "up", "-d", "--quiet-pull"]
        try:
            logger.info(f"Starting environment {name} via docker-compose")
            logger.debug(" ".join(cmd))
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to start environment {name}.")
            raise

    def pause(self, name: str):
        """Pause, the specified environment"""
        cmd = ["docker-compose", "-f", self._envfile, "pause"]
        try:
            logger.info(f"Pausing environment {name}")
            logger.debug(" ".join(cmd))
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to pause environment {name}")
            raise

    def unpause(self, name: str):
        """Unpause, the specified environment"""
        cmd = ["docker-compose", "-f", self._envfile, "unpause"]
        try:
            logger.info(f"Unpausing environment {name}")
            logger.debug(" ".join(cmd))
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to pause environment {name}")
            raise

    def restart(self, name: str):
        """Restart, the specified environment"""
        cmd = ["docker-compose", "-f", self._envfile, "restart"]
        try:
            logger.info(f"Restarting environment {name}")
            logger.debug(" ".join(cmd))
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to restart environment {name}")
            raise

    def stop(self, name: str):
        """Stop the named environment"""
        cmd = ["docker-compose", "-f", self._envfile(name), "rm", "-s", "-f"]
        try:
            logger.info(f"Starting environment {name} via docker-compose")
            logger.debug(" ".join(cmd))
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to stop environment {name}")
            raise
