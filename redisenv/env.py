import json
import os
import subprocess
from typing import Dict, List, Optional

import jinja2
import yaml
from loguru import logger

SENTINEL_TYPE = "sentinel"
STANDALONE_TYPE = "standalone"
REPLICAOF_TYPE = "replicaof"
CLUSTER_TYPE = "cluster"


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
            if x[-4:] == ".yml":
                logger.info(x)

    def listports(self, name, output=True):
        """Output the ports (as json) for the specified environment
        Set output to False, if using this in a library"""
        d = yaml.safe_load(open(self._getenv(name)))
        ports = {}
        for k, i in d.get("services").items():
            for p in i["ports"]:
                port = p.split(":")[0]
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
        tenv = jinja2.Environment(loader=tmpl, trim_blocks=True)

        if redistype == STANDALONE_TYPE:
            templatefile = "standalone.tmpl"
        elif redistype == REPLICAOF_TYPE:
            templatefile = "replica.tmpl"
        elif redistype == SENTINEL_TYPE:
            templatefile = "sentinel.tmpl"
        elif redistype == CLUSTER_TYPE:
            templatefile = "cluster.tmpl"

        tmpl = tenv.get_template(templatefile)
        with open(destfile, "w+") as fp:
            logger.debug(f"Writing {destfile}")
            fp.write(tmpl.render(config))

    def start(
        self, name: str, config: Optional[Dict], redistype: str = STANDALONE_TYPE
    ):
        """Start the environment"""
        if config:
            logger.info(f"Generating environment {name}")
            self._generate(name, config, redistype)

        self._start(name)

    def _start(self, name):
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
        cmd = ["docker-compose", "-f", self._envfile(name), "pause"]
        logger.info(f"Pausing environment {name}")

        try:
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to pause environment {name}")
            raise

    def unpause(self, name: str):
        """Unpause, the specified environment"""
        cmd = ["docker-compose", "-f", self._envfile(name), "unpause"]
        logger.info(f"Unpausing environment {name}")

        try:
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to pause environment {name}")
            raise

    def restart(self, name: str):
        """Restart, the specified environment"""
        cmd = ["docker-compose", "-f", self._envfile(name), "restart"]
        try:
            logger.info(f"Restarting environment {name}")
            logger.debug(" ".join(cmd))
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to restart environment {name}")
            raise

    def stop(self, name: str):
        """Stop the named environment, and remove the generated artifacts"""
        cmd = ["docker-compose", "-f", self._envfile(name), "rm", "-s", "-f"]
        try:
            logger.info(f"Starting environment {name} via docker-compose")
            logger.debug(" ".join(cmd))
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to stop environment {name}")
            raise


class SentinelHandler(EnvironmentHandler):
    """A wrapper, specificatlly for sentinel"""

    def _genconfigs(self, env_name, config_file_content):
        """Generate the configuration files for sentinel"""

        count = 1
        for c in config_file_content:
            node_name = f"sentinel{count}"
            confdest = os.path.join(self.envdir, env_name, "configs", str(count))
            os.makedirs(confdest, exist_ok=True)
            count += 1
            with open(os.path.join(confdest, "sentinel.conf"), "w+") as fp:
                fp.write(c)

    def start(self, env_name, config_file_content, config):
        """Generate the sentinel configs, then start it up"""
        self._genconfigs(env_name, config_file_content)
        self._generate(env_name, config, SENTINEL_TYPE)
        self._start(env_name)


class ClusterHandler(EnvironmentHandler):
    """A wrapper, specifically for redis clusters"""

    def _get_clustermap(self, env_name, ports: List = []) -> str:
        nodemapfile = os.path.join(self.envdir, env_name, "configs", "nodemap")
        with open(nodemapfile, "w+") as fp:
            for p in ports:
                fp.write(f"127.0.0.1:{p}\n")
        return nodemapfile

    def _genconfigs(self, env_name: str, config_file_content: Dict):
        """Generate the redis configuration file for the cluster node"""
        for k, v in config_file_content.items():
            confdest = os.path.join(self.envdir, env_name, "configs", k, "redis.conf")
            os.makedirs(os.path.dirname(confdest), exist_ok=True)
            with open(confdest, "w+") as fp:
                fp.write(v)

    def _gen_cluster_script(self, env_name: str, ports: List, replicas: int) -> str:

        cluster_script = os.path.join(self.envdir, env_name, "start_cluster.sh")

        config = {
            "ports": ports,
            "replicas": replicas,
        }
        here = os.path.join(os.path.dirname(__file__), "templates")

        # add the environment here
        tmpl = jinja2.FileSystemLoader(searchpath=here)
        tenv = jinja2.Environment(loader=tmpl, trim_blocks=True)
        tmpl = tenv.get_template("start_cluster.sh.tmpl")
        with open(cluster_script, "w+") as fp:
            logger.debug(f"Writing {cluster_script}")
            fp.write(tmpl.render(config))

        return cluster_script

    def start(self, env_name: str, config_file_content: Dict, config: Dict):
        os.makedirs(os.path.join(self.envdir, env_name, "configs"), exist_ok=True)
        startscript = self._gen_cluster_script(
            env_name, config.get("ports"), config.get("replicas")
        )
        nodemapfile = self._get_clustermap(env_name, config.get("ports"))
        self._genconfigs(env_name, config_file_content)
        config["nodemapfile"] = nodemapfile
        config["startscript"] = startscript
        self._generate(env_name, config, CLUSTER_TYPE)

        self._start(env_name)
