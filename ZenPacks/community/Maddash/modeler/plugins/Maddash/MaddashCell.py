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

import re
import json
import urllib
import urllib2
from pprint import pformat

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin


class MaddashCell(PythonPlugin):
    relname = 'maddashCells'
    modname = "ZenPacks.community.Maddash.MaddashCell"

    deviceProperties = PythonPlugin.deviceProperties

    def collect(self, device, log):
        log.info('Starting to collect dashboard data from Maddash API')

        rm = self.relMap()

        dashboards_url = 'http://'+ device.manageIp +'/maddash/dashboards'
        
        res = urllib2.urlopen(dashboards_url)
        dashboards = json.loads(res.read())
        #log.debug('dashboards: %s\n\n' % pformat(dashboards))
        for dashboard in dashboards['dashboards']:
            dashboard_name = dashboard['name']
            #log.debug('dashboard: %s\n%s\n\n' % (dashboard_name,pformat(dashboard)))
        
            for grid in dashboard['grids']:
                grid_name = grid['name']
                grid_url = 'http://' + device.manageIp + grid['uri']
                res = urllib2.urlopen(grid_url)
                grid_info = json.loads(res.read())
                #log.debug('\n\ngrid %s:\n%s' % (grid_name,pformat(grid_info))) 
        
                check_name = []
                for cn in grid_info['checkNames']:
                    check_name.append(cn)
        
                row_index = 0
                for row in grid_info['rows']:
                    row_name = row['name']
                    column_index = 0
                    for column_name in grid_info['columnNames']:
                        if grid_info['grid'][row_index][column_index] is not None:
                            check_name_index = 0
                            for check in grid_info['grid'][row_index][column_index]:
                                title = '%s %s %s %s' % (grid_name, row_name, column_name, check_name[check_name_index])
                                log.info('found %s' % title)
                                check_type = 'unknown'
                                check_direction = 'forward'
                                m = re.search(r'^(Throughput|Packet Loss|Latency)', grid_name, re.IGNORECASE)
                                if m:
                                    check_type = m.group(1).lower()
                                m = re.search(r' Reverse$', check_name[check_name_index], re.IGNORECASE)
                                if m:
                                    check_direction = 'reverse'
                                rm.append(self.objectMap({
                                     'id' : self.prepId('%s' % title),
                                     'title' : title,
                                     'check_type' : check_type,
                                     'check_direction' : check_direction,
                                     'check_uri' : 'http://'+ device.manageIp +check['uri']}))
                                check_name_index = check_name_index + 1
                        column_index = column_index + 1
                    row_index = row_index + 1
        return(rm)


    def process(self, device, results, log):
        return results

