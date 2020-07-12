====================================
Backtest documentation
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Quick start
===========

The following will execute the backtest after loading configuration
file, ``config.json`` in same directory. Additional information will be added.

.. code:: bash

    $ backtest [--config config.json]

Sample content of ``config.json``

.. code:: json

    {
        "market": "korea",
        "strategy": "dummy",
        "ticks_dir": "ticks",
        "ledger_dir": "ledger",
        "cash": 1000000
    }


Basic concepts
==============

.. toctree::
    :caption: Basic concepts
    :hidden:

    topics/architecture
    topics/fetcher
    topics/analyzer
    topics/broker
    topics/reporter

:doc:`topics/architecture'
    Architecture

:doc:`topics/fetcher`
    Fetcher

:doc:`topics/analyzer'
    Analyzer

:doc:`topics/broker'
    Broker

:doc:`topics/reporter'
    Reporter


Developing strategy
===================

.. toctree::
    :caption: Developing strategy
    :hidden:

:doc:`topics/jupyter-notebook`
    testing on `Jupyter Notebook`_





Testing
=======

Test codes are located in *tests/* based on
`PyTest <https://docs.pytest.org/en/latest/>`__ framework.


