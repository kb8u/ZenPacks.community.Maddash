"""Get data from Maddash"""

# Logging
import logging
LOG = logging.getLogger('zen.Maddash')

import pprint

# stdlib Imports
import json
import time

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

# PythonCollector Imports
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import (
    PythonDataSourcePlugin,
    )


class Alerts(PythonDataSourcePlugin):

    """Weather Underground alerts data source plugin."""

    @classmethod
    def config_key(cls, datasource, context):
        LOG.debug('################### running config_key')
        return (
            context.device().id,
            datasource.getCycleTime(context),
            'maddash-alerts',
            )

    @inlineCallbacks
    def collect(self, config):
        LOG.debug('running collect on %s', config.id)
        rval = self.new_data()
        try:
            grids_response = yield getPage('http://' + config.id + '/maddash/grids')
            grids = json.loads(grids_response)
            for grid in grids['grids']:
                grid_response = yield getPage('http://' + config.id + grid['uri'])
                grid_data = json.loads(grid_response)
                LOG.debug('retrieved grid data: %s' % pprint.pformat(grid_data))
#                rval.append(grid_data)
        except Exception:
            LOG.exception('failed to get data for %s' % config.id)

        returnValue(rval)

