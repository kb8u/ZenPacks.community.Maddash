==============================
ZenPacks.community.Maddash README.rst
==============================

About
=====

This ZenPack provides monitoring of loss, latency, and throughput measurements, and events from
a `MaDDash <https://software.es.net/maddash/index.html>`_ dashboard configured to monitor a mesh of `perfSONAR <https://www.perfsonar.net>`_ network performance measurement nodes.

Requirements
============

Zenoss
------

You must first have, or install, Zenoss 2.5.2 or later and have the ZenPacks.zenoss.ZenPackLib and Zenpacks.zenoss.PythonCollector zenpacks installed.  This zenpack was tested against Zenoss 4.2.5


Installation
============

Normal Installation (packaged egg)
----------------------------------

Download the `Maddash ZenPack <http://wiki.zenoss.org/ZenPack:Maddash>`_.
Install the zenpack through the zenoss GUI and restart zenoss, or copy the .egg file to your Zenoss server and run the following commands as the zenoss user.

    ::

        zenpack --install ZenPacks.community.Maddash-1.0.0.egg
        zenoss restart

Developer Installation (link mode)
----------------------------------

If you wish to further develop and possibly contribute back to the
Maddash ZenPack you should clone the git
`repository <https://github.com/kb8u/ZenPacks.community.Maddash>`_,
then install the ZenPack in developer mode using the following commands.

    ::

        git clone git://github.com/kb8u/ZenPacks.community.Maddash.git
        zenpack --link --install ./ZenPacks.community.Maddash
        zenoss restart


Usage
=====

Installing the ZenPack will add the following items to your Zenoss system.

Device Class
------------

- Network/MadDash

Event Class
-----------

- Net/Performance

Modeler Plugins
---------------

- **Maddash.MaddashCell** - Maddash dashboard cell modeler plugin.

Monitoring Templates
--------------------

- Network/Maddash/latency
- Network/Maddash/packet_loss
- Network/Maddash/throughput
