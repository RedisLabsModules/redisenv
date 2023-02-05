from typing import List, Dict
from .util import free_ports
import jinja2
import os


_default_options = {
    "_nodes": 1,
    "_version": "6.2.8",
    "_image": "redis",
    "_ipv6": False,
    "_docker_host_ip": "172.0.0.1",
}


def genstandalonespec(
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


def genreplicaspec(
    name: str,
    nodes: int = _default_options["_nodes"],
    version: str = _default_options["_version"],
    image: str = _default_options["_image"],
    mounts: List = [],
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


def gensentinelspec(
    name: str,
    nodes: int = _default_options["_nodes"],
    version: str = _default_options["_version"],
    image: str = _default_options["_image"],
    mounts: List = [],
    redisconf: str = "",
    sentinelconfs: List = [],
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
    d["sentineloptions"] = sentinelconfs
    d["mounts"] = []
    for m in mounts:
        d["mounts"].append({"local": m[0], "remote": m[1]})

    if ports != []:
        d["ports"] = ports
    else:
        d["ports"] = free_ports(nodes)

    return d


def gensentinelconf(
    ports: List,
    user: str,
    password: str,
    sentinelopts: List = [],
    templatefile: str = None,
):
    here = os.path.join(os.path.dirname(__file__), "templates")
    if templatefile is None:
        tmpl = jinja2.FileSystemLoader(searchpath=here)
        tenv = jinja2.Environment(loader=tmpl)
    else:
        tenv = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
            open(templatefile).read()
        )
    if templatefile is None:
        tmpl = tenv.get_template("sentinel.conf.tmpl")

    conffiles = []
    for p in ports[1:]:
        context = {
            "sentinelport": p,
            "port": ports[0],
            "sentinel_user": user,
            "sentinel_password": password,
            "sentinelopts": sentinelopts,
        }
        conffiles.append(tmpl.render(context))
    return conffiles
