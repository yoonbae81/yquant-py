Backtest
========

|PyPI version| |Python version| |Test| |Build| |Coverage| |Docs| |License: GPL v3|

A backtest engine for developing algorithmic trading strategy.

Table of Contents
-----------------

-  `Backtest <#backtest>`__
-  `Table of Contents <#table-of-contents>`__
-  `Installation <#installation>`__
-  `Usage <#usage>`__
-  `Support <#support>`__
-  `Contributing <#contributing>`__
-  `Testing <#testing>`__

Installation
------------

.. code:: bash

    $ pip install backtest

Usage
-----

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

Support
-------

Please `open an
issue <https://github.com/yoonbae81/backtest/issues/new>`__ for support.

Contributing
------------

Please contribute using `Github
Flow <https://guides.github.com/introduction/flow/>`__. Create a branch,
add commits, and `open a pull
request <https://github.com/yoonbae/backtest/compare/>`__.

Testing
-------

Test codes are located in *tests/* based on
`PyTest <https://docs.pytest.org/en/latest/>`__ framework.

.. |PyPI version| image:: https://img.shields.io/pypi/v/backtest.svg
   :target: https://pypi.org/project/backtest/
.. |Python version| image:: https://img.shields.io/pypi/pyversions/backtest.svg
   :target: https://pypi.org/project/backtest/
.. |Test| image:: https://github.com/yoonbae81/backtest/workflows/test/badge.svg
   :target: https://github.com/yoonbae81/backtest/actions?query=workflow%3Atest
.. |Build| image:: https://github.com/yoonbae81/backtest/workflows/build/badge.svg
   :target: https://github.com/yoonbae81/backtest/actions?query=workflow%3Abuild
.. |Coverage| image:: https://codecov.io/gh/yoonbae81/backtest/graph/badge.svg
   :target: http://codecov.io/gh/yoonbae81/backtest
.. |Docs| image:: https://readthedocs.org/projects/backtest/badge/?version=latest
   :target: https://backtest.readthedocs.io/latest
.. |License: GPL v3| image:: https://img.shields.io/badge/License-GPLv3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0
