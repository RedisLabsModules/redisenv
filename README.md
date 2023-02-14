# redisenv

A library to make it easy to run redis instances. This tool is a wrapper around [docker](https://docs.docker.com) and [docker-compose](https://docs.docker.com/compose/), and runs all instances within docker.

[![CI](https://github.com/RedisLabsModules/redisenv/actions/workflows/integration.yml/badge.svg)](https://github.com/RedisLabsModules/redisenv/actions/workflows/integration.yml)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE
[![pypi](https://badge.fury.io/py/redisenv.svg)](https://pypi.org/project/redisenv/)


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
redisenv --name foo create -n 1
```

Start an environment with the redisbloom module, downloaded into a folder named modules. Note - you need the full *local* path to the directory.

```bash
redisenv --name foo create -n 1 -M `pwd`/modules /modules -o "--loadmodule /modules/redisbloom.so"
```

Destroy the environment named foo:

```bash
redisenv --name foo destroy
```