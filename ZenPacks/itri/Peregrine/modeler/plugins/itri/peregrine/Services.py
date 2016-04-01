"""Models Peregrine services using the Peregrine API."""

# stdlib Imports
import json
import urllib

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

class Services(PythonPlugin):
    """Peregrine services modeler plugin."""

    requiredProperties = (
        'zPeregrinePort',
    )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        """ Asynchronously collect data from device. Return a deferred"""

        results = {}
        
        log.info("%s: Collecting data...", device.id)
        
        # Get the API port and validate it if it's set
        peregrine_port = getattr(device, 'zPeregrinePort', None)
        if not peregrine_port:
            log.error("%s: %s not set. Please set port to connect to the Peregrine API")
            returnValue(None)
        
        # Get the Peregrine API base URL
        base_url = 'http://' + device.id + ':' + peregrine_port + '/controller/nb/v3/peregrinepm'
        
        # Get the Peregrine Services
        results['services'] = []
        try:
            services = yield getPage(base_url + '/showStatus')
            services = jsonloads(services)
            #results['services'] = ...
        except Exception, e:
            log.error("%s: %s", device.id, e)
            returnValue(None)
        
        log.debug("Peregrine Services: %s\n" % str(services))
        
        returnValue(results)
    
    def process(self, device, results, log):
        """ Process results. Return iterable of datamaps or None."""
        
        log.info("%s: Processing data...", device.id)
        
        # Process services
        services = []
        for service in results['services']:
            services.append(ObjectMap(
                modname='ZenPacks.itri.Peregrine.PeregrineService',
                data=dict(
                    id=prepId(''),
                    title= '',
                    agent= '',
                    status= '',
                )))
                
        return None
