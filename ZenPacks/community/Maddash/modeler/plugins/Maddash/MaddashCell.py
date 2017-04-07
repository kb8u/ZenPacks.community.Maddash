#####################################################################
#
# Model a Maddash device using json API
#
# Copyright (C) 2017 Russell Dwarshuis, Merit Network, Inc.
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
#####################################################################

__doc__="""MaddashDeviceModeler gets the dashboards available from a system running the Maddash JSON API."""

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
import json
import urllib
import urllib2
from pprint import pformat


class MaddashCell(PythonPlugin):

    relname = 'maddashCell'
    modname = "ZenPacks.community.Maddash.MaddashCell"

    def collect(self, device, log):
        log.info('Starting to collect dashborad data from Maddash API')

        dashboards = ''
        url = 'http://'+ device.manageIp +'/maddash/dashboards'

        # call JSON API and return result
        try:
#            req.add_header('Content-type', 'application/json; charset=utf-8')
            res = urllib2.urlopen(url)
            dashboards = res.read()
            log.debug('API returned: %s' % pformat(dashboards))
        except:
            log.error('Error reading: %s' % url) 
            return(None)

        rm = self.relMap()

        rm.append(self.objectMap({'dashboards':dashboards}))

        return(rm)

    def process(self, device, results, log):
        return results

