import json
import os
import subprocess
from typing import Dict, List, Optional
from .util import free_ports

import jinja2
import yaml
from loguru import logger

SENTINEL_TYPE = "sentinel"
STANDALONE_TYPE = "standalone"
REPLICAOF_TYPE = "replicaof"
CLUSTER_TYPE = "cluster"


_default_options = {
    "_nodes": 1,
    "_version": "6.2.8",
    "_image": "redis",
    "_ipv6": False,
    "_docker_host_ip": "172.0.0.1",
    "_cluster_replicas": 1,
}


class EnvironmentHandler:
    """Environment"""

    def __init__(self, destdir: str, env_name: str, disable_logging=False):
        self._ENVDIR = destdir
        self._ENVNAME = env_name
        os.makedirs(self.envdir, exist_ok=True)
        os.makedirs(self.envconfigdir, exist_ok=True)
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

    def listports(self, output=True):
        """Output the ports (as json) for the specified environment
        Set output to False, if using this in a library"""
        if not os.path.isfile(self.envfile):
            logger.critical(f"There is no environment in {self.envfile}")
            return

        d = yaml.safe_load(open(self.envfile))
        ports = {}
        for k, i in d.get("services").items():
            for p in i["ports"]:
                port = p.split(":")[0]
                ports[k] = {"port": port, "connstr": f"redis://localhost:{port}"}

        if output:
            print(json.dumps(ports))
        return ports

    @property
    def envdir(self):
        return self._ENVDIR

    @property
    def envname(self):
        return self._ENVNAME

    @property
    def envfile(self):
        return os.path.join(self.envdir, f"{self.envname}.yml")

    @property
    def envconfigdir(self):
        cfg = os.path.join(self.envdir, self.envname, "configs")
        os.makedirs(cfg, exist_ok=True)
        return cfg

    def _generate(self, template: str, context: dict = {}, dest=None):

        here = os.path.join(os.path.dirname(__file__), "templates")
        fsl = jinja2.FileSystemLoader(searchpath=here)
        tenv = jinja2.Environment(loader=fsl, trim_blocks=True)
        tmpl = tenv.get_template(template)
        if dest:
            with open(dest, "w+") as fp:
                logger.debug(f"Writing {dest}")
                fp.write(tmpl.render(context))

        return tmpl.render(context)

    def start(self, config: Optional[Dict], redistype: str = STANDALONE_TYPE):
        """Start the environment"""

        if redistype == STANDALONE_TYPE:
            templatefile = "standalone.tmpl"
        elif redistype == REPLICAOF_TYPE:
            templatefile = "replica.tmpl"
        elif redistype == SENTINEL_TYPE:
            templatefile = "sentinel.tmpl"
        elif redistype == CLUSTER_TYPE:
            templatefile = "cluster.tmpl"
        if config:
            self._generate(templatefile, config, self.envfile)

        self._start()

    def _start(self):
        cmd = ["docker-compose", "-f", self.envfile, "up", "-d", "--quiet-pull"]
        try:
            logger.info(f"Starting environment {self.envname} via docker-compose")
            logger.debug(" ".join(cmd))
            subprocess.run(cmd, check=True)
        except:
            logger.critical(f"Failed to start environment {self.envname}.")
            raise


class StandaloneHandler(EnvironmentHandler):
    """Redis Standalone"""

    def gen_spec(
        self,
        name: str,
        nodes: int = _default_options["_nodes"],
        version: str = _default_options["_version"],
        image: str = _default_options["_image"],
        mounts: List = [],
        conffile: str = "",
        ipv6: bool = _default_options["_ipv6"],
        redisopts: List = [],
    ) -> Dict:
        """Generate the environment spec, used in generating the
        docker-compose configuration.
        """
        d = {"name": name}
        d["nodes"] = nodes
        d["version"] = version
        d["listening_port"] = 6379
        d["conffile"] = conffile
        d["ipv6"] = ipv6
        d["image"] = image
        d["redisoptions"] = redisopts
        d["ports"] = free_ports(nodes)

        d["mounts"] = []
        for m in mounts:
            d["mounts"].append({"local": m[0], "remote": m[1]})

        return d


class ReplicaHandler(EnvironmentHandler):
    """Redis replicas"""

    def gen_spec(
        self,
        name: str,
        nodes: int = _default_options["_nodes"],
        version: str = _default_options["_version"],
        image: str = _default_options["_image"],
        mounts: list = [],
        conffile: str = "",
        ipv6: bool = _default_options["_ipv6"],
        redisopts: List = [],
        replicaof: int = -1,
        dockerhost: str = None,
    ) -> Dict:
        """Generate the environment spec, used in generating the
        docker-compose configuration.
        """
        d = {"name": name}
        d["nodes"] = nodes
        d["version"] = version
        d["listening_port"] = 6379
        d["conffile"] = conffile
        d["ipv6"] = ipv6
        d["image"] = image
        d["docker_host"] = dockerhost
        d["redisoptions"] = redisopts
        d["ports"] = free_ports(nodes)
        d["replicaof"] = replicaof

        d["mounts"] = []
        for m in mounts:
            d["mounts"].append({"local": m[0], "remote": m[1]})

        return d


class SentinelHandler(EnvironmentHandler):
    """A wrapper, specificatlly for sentinel"""

    def _write_configs(self, config_file_content):
        """Generate the configuration files for sentinel"""

        count = 1
        for c in config_file_content:
            node_name = f"sentinel{count}"
            confdest = os.path.join(self.envconfigdir, str(count))
            os.makedirs(confdest, exist_ok=True)
            count += 1
            with open(os.path.join(confdest, "sentinel.conf"), "w+") as fp:
                fp.write(c)

    def gen_spec(
        self,
        name: str,
        nodes: int = _default_options["_nodes"],
        version: str = _default_options["_version"],
        image: str = _default_options["_image"],
        mounts: List = [],
        redisconf: str = "",
        redisopts: List = [],
        ports: List = [],
    ) -> Dict:
        """Generate the sentinel environment spec, and conf file."""

        d = {"name": name}
        d["nodes"] = nodes
        d["version"] = version
        d["listening_port"] = 6379
        d["sentinel_port"] = 26379
        d["redisconf"] = redisconf
        d["image"] = image
        d["redisoptions"] = redisopts

        d["mounts"] = []
        for m in mounts:
            d["mounts"].append({"local": m[0], "remote": m[1]})

        if ports != []:
            d["ports"] = ports
        else:
            d["ports"] = free_ports(nodes)

        return d

    def gen_config(
        self,
        ports: List,
        user: str,
        password: str,
        sentinelopts: List = [],
        docker_ip: str = "",
    ) -> List:
        here = os.path.join(os.path.dirname(__file__), "templates")
        fsl = jinja2.FileSystemLoader(searchpath=here)
        tenv = jinja2.Environment(loader=fsl, trim_blocks=True)
        tmpl = tenv.get_template("sentinel.conf.tmpl")

        conffiles = []
        for p in ports[1:]:
            context = {
                "dockerhost": docker_ip,
                "sentinelport": p,
                "port": ports[0],
                "sentinel_user": user,
                "sentinel_password": password,
                "sentinelopts": sentinelopts,
            }
            conffiles.append(tmpl.render(context))
        return conffiles

    def start(self, config_file_content, config):
        """Generate the sentinel configs, then start it up"""
        self._write_configs(config_file_content)
        self._generate("sentinel.tmpl", config, self.envfile)
        self._start()


class ClusterHandler(EnvironmentHandler):
    """A wrapper, specifically for redis clusters"""

    def gen_config(
        self,
        ports: List,
        redisopts: List = [],
    ) -> Dict:
        """Generates the cluster configuration file contents,
        per cluster node"""

        conffiles = {}
        for p in ports:
            context = {"port": p, "redisopts": redisopts}
            res = self._generate("cluster.conf.tmpl", context, None)
            conffiles[str(p)] = res
        return conffiles

    def gen_spec(
        self,
        nodes: int = _default_options["_nodes"],
        version: str = _default_options["_version"],
        image: str = _default_options["_image"],
        mounts: List = [],
        ports: List = [],
        replicas: int = _default_options["_cluster_replicas"],
    ):
        """Generate the docker-compose variables for the specified
        cluster configuration."""
        d = {"name": self.envname}
        d["nodes"] = nodes
        d["version"] = version
        d["image"] = image
        d["mounts"] = []
        d["ports"] = ports
        d["replicas"] = replicas
        for m in mounts:
            d["mounts"].append({"local": m[0], "remote": m[1]})

        return d

    def _get_clustermap(self, ports: List = []) -> str:
        nodemapfile = os.path.join(self.envconfigdir, "nodemap")
        with open(nodemapfile, "w+") as fp:
            for p in ports:
                fp.write(f"127.0.0.1:{p}\n")
        return nodemapfile

    def _write_configs(self, config_file_content: Dict):
        """Generate the redis configuration file for the cluster node"""
        for k, v in config_file_content.items():
            confdest = os.path.join(self.envconfigdir, k, "redis.conf")
            os.makedirs(os.path.dirname(confdest), exist_ok=True)
            with open(confdest, "w+") as fp:
                fp.write(v)

    def _gen_cluster_script(self, ports: List, replicas: int) -> str:

        cluster_script = os.path.join(self.envdir, self.envname, "start_cluster.sh")

        config = {
            "ports": ports,
            "replicas": replicas,
        }
        self._generate("start_cluster.sh.tmpl", config, cluster_script)

        return cluster_script

    def start(self, config_file_content: Dict, config: Dict):
        startscript = self._gen_cluster_script(
            config.get("ports"), config.get("replicas")
        )
        nodemapfile = self._get_clustermap(config.get("ports"))
        self._write_configs(config_file_content)
        config["nodemapfile"] = nodemapfile
        config["startscript"] = startscript
        self._generate("cluster.tmpl", config, self.envfile)

        self._start()
