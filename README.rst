========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - | |travis| |appveyor|
        | |codecov|
    * - package
      - | |commits-since|

.. |travis| image:: https://api.travis-ci.org/iotanbo/templgen.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/iotanbo/templgen

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/iotanbo/templgen?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/iotanbo/templgen

.. |codecov| image:: https://codecov.io/github/iotanbo/templgen/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/iotanbo/templgen

.. |commits-since| image:: https://img.shields.io/github/commits-since/iotanbo/templgen/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/iotanbo/templgen/compare/v0.0.0...master



.. end-badges

Code generator from templates

* Free software: MIT license

Installation
============

::

    pip install templgen

You can also install the in-development version with::

    pip install https://github.com/iotanbo/templgen/archive/master.zip


Documentation
=============


To use the project:

.. code-block:: python

    import templgen
    templgen.longest()


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
