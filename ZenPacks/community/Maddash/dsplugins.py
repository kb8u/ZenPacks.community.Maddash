"""Get data from Maddash"""

import logging
import re
from pprint import pformat
import json
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import PythonDataSourcePlugin
from Products.ZenUtils.Utils import prepId


LOG = logging.getLogger('zen.Maddash')


class QueryMaddash(PythonDataSourcePlugin):
    """Collect performance data and events from Maddash API"""

    @classmethod
    def config_key(cls, datasource, context):
        return (
            context.device().id,
            datasource.getCycleTime(context),
            'maddash-alerts',
            )

    # maddash api has last data (in a string) and events in a dashboard
    @inlineCallbacks
    def collect(self, config):
        LOG.info('running collect on %s', config.id)

        rval = self.new_data()

        try:
            res =  yield getPage('http://' + config.id + '/maddash/dashboards')
            dashboards = json.loads(res)
            #LOG.debug('dashboards: %s\n\n' % pformat(dashboards))
            for dashboard in dashboards['dashboards']:
                dashboard_name = dashboard['name']
                #LOG.debug('dashboard: %s\n%s\n\n' % (dashboard_name,pformat(dashboard)))

                for grid in dashboard['grids']:
                    grid_name = grid['name']
                    grid_url = 'http://' + config.id + str(grid['uri'])

                    res = yield getPage(grid_url)
                    grid_info = json.loads(res)
                    #LOG.debug('\n\ngrid %s:\n%s' % (grid_name,pformat(grid_info))) 

                    # process performance data from API
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
                                    quantity = 'NaN' # maddash measurement value
                                    title = '%s %s %s %s' % (grid_name, row_name, column_name, check_name[check_name_index])
                                    LOG.debug('found %s' % title)
                                    component_id = prepId(title)
                                    check_uri = str(check['uri'])
                                    # alternate measurement direction on check_name_index
                                    direction_index = check_name_index & 1
                                    check_name_index = check_name_index + 1
                                    message_match = re.search(
                                      '\s+(\d+\.?\d+)(.*)',
                                      str(grid_info['grid'][row_index][column_index][direction_index]['message']))
                                    if message_match:
                                        time = int(grid_info['grid'][row_index][column_index][direction_index]['prevCheckTime'])
                                        quantity = float(message_match.group(1))
                                        units = message_match.group(2)
                                        units_match = re.search('([KMG])[bp]ps',units,re.I)
                                        if units_match:
                                            multiplier = {}
                                            multiplier['k'] = multiplier['K'] = 1e3
                                            multiplier['m'] = multiplier['M'] = 1e6
                                            multiplier['g'] = multiplier['G'] = 1e9
                                            multiplier['t'] = multiplier['T'] = 1e12
                                            try:
                                                quantity = quantity * multiplier[units_match.group(1)]
                                            except KeyError:
                                                pass
                                        # another units_match for latency here
                                        # TODO: code latency munging
                                        LOG.debug('saw quantity % f' % quantity)
                                    
                                        rval['values'][component_id]['measurement'] = (quantity,time) 
                            column_index = column_index + 1
                        row_index = row_index + 1
                    
                    # process event data from API
                    event_type = grid_info['name']
                    report = grid_info['report']
                    for site_name in report['sites']:
                        site = report['sites'][site_name]
                        if 'problems' in site:
                            for problem in site['problems']:
                                LOG.info('found problem, severity: %d' % problem['severity'])
                                event = {
                                  'device': config.id,
                                  'component' : '%s %s' % (event_type, site_name),
                                  'severity' : self.__API_severity(problem['severity']),
                                  'eventKey' : '%s %s' % (event_type, site_name),
                                  'eventClassKey' : 'Maddash',
                                  'summary' : '%s %s: %s' % (site_name, event_type, problem['name']),
                                  'message' : '%s %s: %s' % (site_name, event_type, problem['name'])
                                }
                                rval['events'].append(event)
                        # clear event if there is no 'problems' key, an OK count, and no WARN or CRITICAL in stats
                        else:
                            if site['stats'][0] > 0 and site['stats'][1] == 0 and site['stats'][2] == 0:
                                #LOG.debug('clear event for %s %s' % (event_type, site_name))
                                rval['events'].append({
                                  'device': config.id,
                                  'component' : '%s %s' % (event_type, site_name),
                                  'severity' : 0,
                                  'eventKey' : '%s %s' % (event_type, site_name),
                                  'eventClassKey' : 'Maddash',
                                  'summary' : 'no problems',
                                  'message' : 'no problems'
                                })
                                continue
                            if site['stats'][1]:
                                rval['events'].append({
                                  'device': config.id,
                                  'component' : '%s %s' % (event_type, site_name),
                                  'severity' : 4,
                                  'eventKey' : '%s %s' % (event_type, site_name),
                                  'eventClassKey' : 'Maddash',
                                  'summary' : 'One or more sites has %s' % grid_info['statusLabels'][1],
                                  'message' : 'One or more sites has %s' % grid_info['statusLabels'][1]
                                })
                            if site['stats'][2]:
                                rval['events'].append({
                                  'device': config.id,
                                  'component' : '%s %s' % (event_type, site_name),
                                  'severity' : 5,
                                  'eventKey' : '%s %s' % (event_type, site_name),
                                  'eventClassKey' : 'Maddash',
                                  'summary' : 'One or more sites has %s' % grid_info['statusLabels'][2],
                                  'message' : 'One or more sites has %s' % grid_info['statusLabels'][2]
                                })

        except Exception:
            LOG.exception('failed to get data for %s' % config.id)

        #LOG.debug('rval:\n%s' % pformat(rval))
        returnValue(rval)

    def __API_severity(self, severity):
        if severity == 2:
            return 5
        if severity == 1:
            return 4
        return 0
