.. _manual-installation:

============
Installation
============

---------
Using Pip
---------

Install ``varfish-cli`` into a new virtualenv:

.. code-block:: bash

    virtualenv venv
    source venv/bin/activate
    pip install varfish-cli
    varfish-cli --help

-----------
Using Conda
-----------

You can install VarFish via `bioconda <https://bioconda.github.io>`__

.. code-block:: bash

    ## OR use "conda" below instead of mamba
    mamba create -y -n varfish-cli varfish-cli
    conda activate varfish-cli
    varfish-cli --help

----------------------
Creating Configuration
----------------------

You must create a configuration file at ``~/.varfishrc.toml`` with the URL to the server and the API token that you previously created.
The following Bash snippet creaets such a file:

... code-block:: bash

    cat >~/.varfishrc.toml <<EOF
    [global]

    # URL to VarFish server.
    varfish_server_url = "https://varfish.example.com/"
    # API token to use for VarFish API.
    varfish_api_token = "XXX"
    EOF
