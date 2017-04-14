#!/opt/zenoss/bin/python

import json
import urllib
import urllib2
from pprint import pformat

ip = '192.122.200.131'

dashboards_url = 'http://'+ ip +'/maddash/dashboards'

res = urllib2.urlopen(dashboards_url)
dashboards = json.loads(res.read())
#print 'dashboards: %s\n\n' % pformat(dashboards)
for dashboard in dashboards['dashboards']:
    dashboard_name = dashboard['name']
    #print 'dashboard: %s\n%s\n\n' % (dashboard_name,pformat(dashboard))

    for grid in dashboard['grids']:
        grid_name = grid['name']
        grid_url = 'http://' + ip + grid['uri']
        res = urllib2.urlopen(grid_url)
        grid_info = json.loads(res.read())
        #print '\n\ngrid %s:\n%s' % (grid_name,pformat(grid_info)) 

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
                        print '%s %s %s\n   %s' % (row_name,
                                                   column_name,
                                                   check_name[check_name_index],
                                                   check['uri'])
                        check_name_index = check_name_index + 1
                column_index = column_index + 1
            row_index = row_index + 1
