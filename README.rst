Overview
========

|License| |Build| |Coverage| |Quality|

The **of_l2ls** application is used in basic operation of switches. It
implements the algorithm known as L2 Learning Switch, which aims to figure out
which host is attached to which switch port. The switch keeps a table that
stores a tuple containing the mac address (hardware address) and port number.
So, the switch can forward the packets directly to the destination host.
Initially this table is empty, so the first step, when a host tries to send a
packet to another host, is to add an entry pointing to the source host. Next,
the switch sends the packet to all ports, except to the port of the source
host. The destination host will answer to that packet and once the packet is
received, the switch adds an entry to the table mapping the mac address of the
destination host to a port. This process is repeated until all ports with a
host connected are mapped. This algorithm can be used to update the table when
a change is detected. 

Installing
==========

All of the Kytos Network Applications are located in the NApps online
repository. To install this NApp, run:

.. code:: shell

   $ kytos napps install kytos/of_l2ls

Advanced
========

L2 Learning Switch Operation
----------------------------

At the switch startup, it does not know which hosts are attached to its ports.
So, when some host A sends a frame addressed to host B, the switch will
broadcast this frame to all ports, except to the port from where the frame has
arrived. At same time, the switch learns at which port host A is attached. A
table is stored in switch's local memory mapping the host mac address and port
number.

When the host B answers the request, the switch adds to this table an entry
mapping the mac address of host B to the port in which it is connected. This
process goes on until the switch learns which port all hosts are connected.

.. TAGs

.. |License| image:: https://img.shields.io/github/license/kytos/kytos.svg
   :target: https://github.com/kytos/of_l2ls/blob/master/LICENSE
.. |Build| image:: https://scrutinizer-ci.com/g/kytos/of_l2ls/badges/build.png?b=master
  :alt: Build status
  :target: https://scrutinizer-ci.com/g/kytos/of_l2ls/?branch=master
.. |Coverage| image:: https://scrutinizer-ci.com/g/kytos/of_l2ls/badges/coverage.png?b=master
  :alt: Code coverage
  :target: https://scrutinizer-ci.com/g/kytos/of_l2ls/?branch=master
.. |Quality| image:: https://scrutinizer-ci.com/g/kytos/of_l2ls/badges/quality-score.png?b=master
  :alt: Code-quality score
  :target: https://scrutinizer-ci.com/g/kytos/of_l2ls/?branch=master