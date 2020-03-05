#########
Changelog
#########
All notable changes to the kytos-napps project will be documented in this file.

[UNRELEASED] - Under development
*********************************
Added
=====
- Added support for automated tests and CI with Travis.
- Added tags decorator to run tests by type and size.
- Added unit tests.

Changed
=======
- Changed README.rst to include some info badges.
- Changed tests structure to separate unit and integration tests.

Deprecated
==========

Removed
=======

Fixed
=====
- Fixed Scrutinizer coverage error.

Security
========

[1.1.1] - 2019-03-15
********************
Added
=====
- Continuous integration enabled at scrutinizer.

Fixed
=====
- Fixed some linter issues.

[1.1.0] - 2018-06-15
********************
Added
=====
- Added support to use OpenFlow 1.3.

Changed
=======
- Ignore LLDP packages.
- Updating kytos and python-openflow requirements versions.
- Only use buffer_id in packet_out.

Fixed
=====
- Fixed Ghost hosts appearing in web interface.

[1.0.0] - 2017-05-05
********************
Changed
=======
- Installation process of NApps.
- Logging updated to match changes on Kytos project.

Deprecated
==========
- 'author' attribute was renamed to 'username', and will be removed in future
  releases.

Fixed
=====
- Several bug fixes.


[0.2.0] - 2017-03-24
********************
Added
=====
- Python3.6 requirement.
- Individual Settings file.


[0.1.0] - 2016-11-09
********************
Added
=====
- kytos.json file with NApp metadata.
- LICENSE file.
- First version of the NApp.
