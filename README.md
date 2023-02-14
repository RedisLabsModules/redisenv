# redisenv

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![pypi](https://badge.fury.io/py/redisenv.svg)](https://pypi.org/project/redisenv/)
[![CI](https://github.com/RedisLabsModules/redisenv/actions/workflows/integration.yml/badge.svg)](https://github.com/RedisLabsModules/redisenv/actions/workflows/integration.yml)

redisenv is library that makes generating redis test environments easier. This tool generates [docker-compose](https://docs.docker.com/compose/) files, and runs all instances within docker.  Generated docker instances select a random port, based on the available free ports, and when running ```redisenv ports```, a json parseable string of the build connections is outputted.

Currently redisenv supports:

* Redis standalone

* Redis Sentinel

* Redis Clusters

* Redis masters with replicas

----

## Installation

### Requirements

* Python >= 3.7

* docker-compose

* docker

## Usage

List options. Note, each subcommand accepts its own ```--help```

```bash
redisenv --help
```

Start an environment named foo, with one container:

```bash
redisenv --name foo standalone create --nodes 1
```

Start an environment with the redisbloom module, downloaded into a folder named modules. Note - you need the full *local* path to the directory.

```bash
redisenv --name foo standalone create -n 1 -M `pwd`/modules /modules -o "--loadmodule /modules/redisbloom.so"
```

Destroy the environment named foo:

```bash
redisenv --name foo destroy
```
