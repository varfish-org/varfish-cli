[![CI](https://github.com/bihealth/varfish-cli/actions/workflows/main.yml/badge.svg)](https://github.com/bihealth/varfish-cli/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/bihealth/varfish-cli/branch/main/graph/badge.svg?token=9ZX53MPEJT)](https://codecov.io/gh/bihealth/varfish-cli)
[![MIT license](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

# VarFish CLI

Command line interface for [VarFishServer](https://github.com/bihealth/varfish-server).

## Getting Started

- [VarFish Homepage](https://www.cubi.bihealth.org/software/varfish/)
- [Manual](https://varfish-server.readthedocs.io/en/latest/)
    - [Installation Instructions](https://varfish-server.readthedocs.io/en/latest/admin_install.html)
- [Docker Compose Installer](https://github.com/bihealth/varfish-docker-compose#run-varfish-server-using-docker-compose)

## VarFish Repositories

- [varfish-server](https://github.com/bihealth/varfish-server) --
  The VarFish Server is the web frontend used by the end users / data analysts.
- [varfish-annotator](https://github.com/bihealth/varfish-annotator) --
  The VarFish Annotator is a command line utility used for annotating VCF files and converting them to files that can be imported into VarFish Server.
- [varfish-cli](https://github.com/bihealth/varfish-cli) --
  The VarFish Command Line Interface allows to import data through the VarFish REST API.
- [varfish-db-downloader](https://github.com/bihealth/varfish-db-downloader) --
  The VarFish DB Downloader is a command line tool for downloading the background database.
- [varfish-docker-compose](https://github.com/bihealth/varfish-docker-compose) --
  Quickly get started running a VarFish server by using Docker Compose.
  We provide a prebuilt data set with some already imported data.

## Installation

### From Source

```bash
$ git clone git@github.com:bihealth/varfish-cli.git
$ cd varfish-cli
$ conda create -n varfish-cli python=3.7
$ conda activate varfish-cli
$ pip install -e .
$ cat >~/.varfishrc.toml <<EOF
[global]

# URL to VarFish server.
varfish_server_url = "https://varfish.example.com/"
# API token to use for VarFish API.
varfish_api_token = "XXX"
EOF
```

### Using pip


`varfish-cli` is also available as a pip-Package.
Preferably install into a separate venv.

```bash
$ pip install varfish-cli
$ cat >~/.varfishrc.toml <<EOF
[global]

# URL to VarFish server.
varfish_server_url = "https://varfish.example.com/"
# API token to use for VarFish API.
varfish_api_token = "XXX"
EOF
```
