[![CI](https://github.com/bihealth/varfish-cli/actions/workflows/main.yml/badge.svg)](https://github.com/bihealth/varfish-cli/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/bihealth/varfish-cli/branch/main/graph/badge.svg?token=9ZX53MPEJT)](https://codecov.io/gh/bihealth/varfish-cli)
[![MIT license](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

# VarFish CLI

Command line interface for [bihealth/varfish-server](https://github.com/bihealth/varfish-server).

> [!NOTE]
> This repository focuses on the command line interface program `varfish-cli`.
> If you are new to VarFish, you may want to start at the repository [bihealth/varfish-server](https://github.com/bihealth/varfish-server).

## Installation

You can install `varfish-cli` from [bioconda](https://bioconda.github.io/):

To create a new conda environment named `varfish-cli` with the package:

```
mamba create -y -n varfish-cli -c bioconda varfish-cli
conda activate varfish-cli
varfish-cli --help
```

To get help with individual sub commands:

```
varfish-cli importer
# OR
varfish-cli importer --help
```

You will also need to create a configuration file in your home folder with the server address:

```
$ cat >~/.varfishrc.toml <<EOF
[global]

# URL to VarFish server.
varfish_server_url = "https://varfish.example.com/"
# API token to use for VarFish API.
varfish_api_token = "XXX"
EOF
```

## Developer Information

### Development Setup

Preqrequisites:

- Python >=3.10

Clone the repository:

```
git clone git@github.com:bihealth/varfish-cli.git
cd varfish-cli-ng
```

Now, create a virtualenv and install the software and its development requirements:

```
virtualenv venv
source venv/bin/activate

pip install -r requirements/develop.txt
pip install -e .
```

Finally, create the configuration file:

```
$ cat >~/.varfishrc.toml <<EOF
[global]

# URL to VarFish server.
varfish_server_url = "https://varfish.example.com/"
# API token to use for VarFish API.
varfish_api_token = "XXX"
EOF
```

### GitHub Project Management with Terraform

```
export GITHUB_OWNER=bihealth
export GITHUB_TOKEN=ghp_<thetoken>

cd utils/terraform
terraform init
terraform import github_repository.varfish-cli varfish-cli
terraform validate
terraform fmt
terraform plan
terraform apply
```
