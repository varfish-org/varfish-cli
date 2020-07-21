===========
VarFish CLI
===========

------------
Installation
------------

.. code-block:: bash

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
