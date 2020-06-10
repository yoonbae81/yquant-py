====================================
Backtest
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



Usage
=====

The following will execute the backtest after loading configuration
file, ``config.json`` in same directory.

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


Testing
=======

Test codes are located in *tests/* based on
`PyTest <https://docs.pytest.org/en/latest/>`__ framework.
