.. image:: https://github.com/bihealth/varfish-cli/workflows/CI/badge.svg
    :target: https://github.com/bihealth/varfish-cli/actions
    :alt: Continuous Integration Status
.. image:: https://app.codacy.com/project/badge/Grade/83ee38265942489193d6ce8a547eb9f9
    :target: https://www.codacy.com/gh/bihealth/varfish-cli/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/varfish-cli&amp;utm_campaign=Badge_Grade
.. image:: https://app.codacy.com/project/badge/Coverage/83ee38265942489193d6ce8a547eb9f9
    :target: https://www.codacy.com/gh/bihealth/varfish-cli/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/varfish-cli&amp;utm_campaign=Badge_Coverage
.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :alt: MIT License
    :target: https://opensource.org/licenses/MIT

===========
VarFish CLI
===========

Command line interface for [VarFishServer](https://github.com/bihealth/varfish-server)

---------------
Getting Started
---------------

- `VarFish Homepage <https://www.cubi.bihealth.org/software/varfish/>`__
- `Manual <https://varfish-server.readthedocs.io/en/latest/>`__
    - `Installation Instructions <https://varfish-server.readthedocs.io/en/latest/admin_install.html>`__.
- `Docker Compose Installer <https://github.com/bihealth/varfish-docker-compose#run-varfish-server-using-docker-compose>`__.

--------------------
VarFish Repositories
--------------------

`varfish-server <https://github.com/bihealth/varfish-server>`__
    The VarFish Server is the web frontend used by the end users / data analysts.
`varfish-annotator <https://github.com/bihealth/varfish-annotator>`__
    The VarFish Annotator is a command line utility used for annotating VCF files and converting them to files that can be imported into VarFish Server.
`varfish-cli <https://github.com/bihealth/varfish-cli>`__
    The VarFish Command Line Interface allows to import data through the VarFish REST API.
`varfish-db-downloader <https://github.com/bihealth/varfish-db-downloader>`__
    The VarFish DB Downloader is a command line tool for downloading the background database.
`varfish-docker-compose <https://github.com/bihealth/varfish-docker-compose>`__
    Quickly get started running a VarFish server by using Docker Compose.
    We provide a prebuilt data set with some already imported data.

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

---------
Releasing
---------

.. code-block:: bash

    $ $EDITOR HISTORY.rst
    $ git tag ...
    $ rm -rf dist
    $ python setup.py sdist
    $ twine upload dist/*.tar.gz
