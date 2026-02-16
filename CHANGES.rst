CHANGELOG
=========

.. towncrier release notes start

pytest-elasticsearch 5.0.0 (2026-02-16)
=======================================

Breaking changes
----------------

- Replace TypedDict-based config with a dataclass-based config. (`#822 <https://github.com/dbfixtures/pytest-elasticsearch/issues/822>`__)
- Drop support for Python 3.9 (`#828 <https://github.com/dbfixtures/pytest-elasticsearch/issues/828>`__)
- Drop support for elasticsearch older than 8.0 (`#830 <https://github.com/dbfixtures/pytest-elasticsearch/issues/830>`__)


Bugfixes
--------

- Skip system indices during Elasticsearch client fixture cleanup to avoid 403 errors. (`#841 <https://github.com/dbfixtures/pytest-elasticsearch/issues/841>`__)
- Default the noprocess fixture port to 9200 to match Elasticsearch HTTP defaults.


Documentation
-------------

- Documented the pytest-elasticsearch plugin architecture with a new sequence diagram. (`#826 <https://github.com/dbfixtures/pytest-elasticsearch/issues/826>`__)
- Add a quickstart section, prerequisites, and clearer fixture/configuration guidance to the README.


Features
--------

- Improved xdist compatibility by introducing port-locking mechanism.

  If one worker claims a port, it will lock it, and other xdist workers will
  either check another port or raise an error with clear message. (`#823 <https://github.com/dbfixtures/pytest-elasticsearch/issues/823>`__)
- Mark support for Python 3.14 (`#828 <https://github.com/dbfixtures/pytest-elasticsearch/issues/828>`__)


Miscellaneous
-------------

- Run xdist tests on CI with -n auto. (`#823 <https://github.com/dbfixtures/pytest-elasticsearch/issues/823>`__)
- Replace black with ruff-format (`#824 <https://github.com/dbfixtures/pytest-elasticsearch/issues/824>`__)
- Added workflow to run tests against oldest supported dependency versions. (`#825 <https://github.com/dbfixtures/pytest-elasticsearch/issues/825>`__)
- Add check-python-version-consistency to pyproject.

  It'll keep watch over updating supported python version in pyproject.toml (`#827 <https://github.com/dbfixtures/pytest-elasticsearch/issues/827>`__)
- Add release workflow to ease the release process (`#829 <https://github.com/dbfixtures/pytest-elasticsearch/issues/829>`__)
- Split factories into separate submodules. (`#831 <https://github.com/dbfixtures/pytest-elasticsearch/issues/831>`__)
- Add Elasticsearch 9.3 to CI (`#834 <https://github.com/dbfixtures/pytest-elasticsearch/issues/834>`__)
- Updated pytest to version 9 and update it's configuration to be toml native. (`#852 <https://github.com/dbfixtures/pytest-elasticsearch/issues/852>`__)
- Adjust links after repository transfer
- Adjust workflows for actions-reuse 3
- Do not run elasticsearch 8 tests with elasticsearch 9 library.
- Include elasticsearch 9.0, 8.17 and 8.18 in CI.
- Pin elasticsearch 17 tests to ubuntu 22.04, as 24.04 had some issues running elasticsearch 17.
- Use pre-commit for maintaining code style and linting


4.1.1 (2024-12-03)
==================

Breaking changes
----------------

- Dropped support for Python 3.8


Features
--------

- Marked support for Python 3.13


Miscellaneous
-------------

- Update elasticsearch in tests up Until 8.16


4.1.0 (2024-03-15)
==================

Features
--------

- Support python 3.12 (`#609 <https://github.com/dbfixtures/pytest-elasticsearch/issues/609>`__)


Miscellaneous
-------------

- `#582 <https://github.com/dbfixtures/pytest-elasticsearch/issues/582>`__, `#585 <https://github.com/dbfixtures/pytest-elasticsearch/issues/585>`__, `#610 <https://github.com/dbfixtures/pytest-elasticsearch/issues/610>`__, `#611 <https://github.com/dbfixtures/pytest-elasticsearch/issues/611>`__, `#612 <https://github.com/dbfixtures/pytest-elasticsearch/issues/612>`__


4.0.2 (2023-09-13)
==================

Bugfixes
--------

- The current version of pytest-elasticsearch is trying to use pytest.Parser.
  However, pytest.Parser is added only after pytest 7. We should update
  dependencies to use only pytest 7+ (`#522 <https://github.com/dbfixtures/pytest-elasticsearch/issues/522>`__)


4.0.1 (2023-08-03)
==================

Bugfixes
--------

- Fixed compatibility with elasticsearch client 7.x (`#512 <https://github.com/dbfixtures/pytest-elasticsearch/issues/512>`__)


4.0.0 (2023-07-28)
==================

Breaking changes
----------------

- Drop support for elastisearch older than 7 (`#384 <https://github.com/dbfixtures/pytest-elasticsearch/issues/384>`__)
- Dropped support for python 3.7 (`#474 <https://github.com/dbfixtures/pytest-elasticsearch/issues/474>`__)


Features
--------

- Support elasticsearch up to 8.9 (`#384 <https://github.com/dbfixtures/pytest-elasticsearch/issues/384>`__)
- Package is fully typed and mypy checked. (`#474 <https://github.com/dbfixtures/pytest-elasticsearch/issues/474>`__)
- Support Python 3.11 (`#475 <https://github.com/dbfixtures/pytest-elasticsearch/issues/475>`__)


Miscellaneous
-------------

- `#384 <https://github.com/dbfixtures/pytest-elasticsearch/issues/384>`__, `#469 <https://github.com/dbfixtures/pytest-elasticsearch/issues/469>`__, `#470 <https://github.com/dbfixtures/pytest-elasticsearch/issues/470>`__, `#471 <https://github.com/dbfixtures/pytest-elasticsearch/issues/471>`__, `#472 <https://github.com/dbfixtures/pytest-elasticsearch/issues/472>`__, `#473 <https://github.com/dbfixtures/pytest-elasticsearch/issues/473>`__, `#476 <https://github.com/dbfixtures/pytest-elasticsearch/issues/476>`__, `#484 <https://github.com/dbfixtures/pytest-elasticsearch/issues/484>`__, `#486 <https://github.com/dbfixtures/pytest-elasticsearch/issues/486>`__, `#488 <https://github.com/dbfixtures/pytest-elasticsearch/issues/488>`__, `#505 <https://github.com/dbfixtures/pytest-elasticsearch/issues/505>`__


3.0.0
=====

Features
--------

- Import FixtureRequest from pytest, not private _pytest.
  Require at least pytest 6.2
- Replace tmpdir_factory with tmp_path_factory

Removals
--------


- Removed `logs_prefix` process fixture parameter, `--elasticsearch-logsdir`
  command parameter and `elasticsearch_logsdir` ini configuration option
- Removed `elasticsearch_logsdir` process fixture parameter `--elasticsearch-logs-prefix`
  command parameter and `elasticsearch_logs_prefix` ini configuration option

Support
-------

- support only elasticsearch 6.x and up, same as the most recent elasticsearch library

Misc
----

- rely on `get_port` functionality delivered by `port_for`

2.1.0
=====

Features
--------

- Add command line and ini configuration option for the executable.
- Require python 3.7 and up
- Unify handling of a temporary directory, now temporary directory holding logs,
  workdir, pid will be named after fixture name.

Deprecations
------------

- Deprecated `logs_prefix` process fixture parameter, `--elasticsearch-logsdir`
  command parameter and `elasticsearch_logsdir` ini configuration option
- Deprecated `elasticsearch_logsdir` process fixture parameter `--elasticsearch-logs-prefix`
  command parameter and `elasticsearch_logs_prefix` ini configuration option

Bugfix
------

- Handle properly elasticsearch versions with two-digit minor version

Misc
----

- Migrated CI/CD to Github Actions
- Blackified Codebase

2.0.1
=====

- [cleanup] Drop support for python versions older than 3.6
- [fix] Adjust for mirakuru 2.2.0 and up


2.0.0
=====

- [enhancement] Created a specified Executor to manage elasticsearch
- [enhancement] added new elasticsearch_nooproc fixture to connect to already
  existing elasticsearch index
- [cleanup] Drop support for unused discovery_zen_ping_multicast
  and elasticsearch_configuration_path option
- [cleanup] Drop support for elasticsearch older than 5
- [cleanup] Drop support for python versions older than 3.5
- [bugfix] changed default index.memory type to mmapfs, over long invalid
  memory type

1.3.0
=====

- [feature] - Support for major elasticsearch versions


1.2.1
=====

- [cleanup] - removed path.py dependency

1.2.0
=====

- [feature] - migrate usage of getfuncargvalue to getfixturevalue. require at least pytest 3.0.0
- [feature] - default logsdir to $TMPDIR
- [feature] - run process on random port by default - enhances xdist experience

1.1.0
=====

- [feature] use tmpfile.gettempdir instead of hardcoded /tmp directory
- [docs] added description to all command line and ini options
- [bugfix] made command line option's dests more distinc, to prevent from influencing other pytest plugins

1.0.0
=====

- [feature] pytest.ini option for every command line option
- [feature] Command line options for every fixture factory argument
- Extracted original code from pytest-dbfixtures
