"""Models Peregrine services using the Peregrine API."""

# stdlib Imports
import json
import urllib
import base64

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.web.client import getPage

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

class Services(PythonPlugin):
    """Peregrine services modeler plugin."""
    
    relname = 'peregrineServices'
    modname = 'ZenPacks.itri.Peregrine.PeregrineService'

    requiredProperties = (
        'zPeregrinePort',
        'zPeregrineUser',
        'zPeregrinePassword',
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
            log.error("%s: %s not set. Please set port to connect to the Peregrine API", device.id, 'zPeregrinePort')
            returnValue(None)
        
        # Get the API user and validate it if it's set
        peregrine_user = getattr(device, 'zPeregrineUser', None)
        if not peregrine_user:
            log.error("%s: %s not set. Please set username to connect to the Peregrine API", device.id, 'zPeregrineUser')
            returnValue(None)
            
        # Get the API password and validate it if it's set
        peregrine_password = getattr(device, 'zPeregrinePassword', None)
        if not peregrine_password:
            log.error("%s: %s not set. Please set password to connect to the Peregrine API", device.id, 'zPeregrinePassword')
            returnValue(None)
        
        # Get the Peregrine API base URL
        base_url = 'http://' + device.id + ':' + peregrine_port + '/controller/nb/v3/peregrinepm'
        
        # Get the Peregrine Services
        results['services'] = []
        try:
            # Build the authentication headers
            basicAuth = base64.encodestring("%s:%s" % (peregrine_user, peregrine_password))
            authHeader = "Basic " + basicAuth.strip()
        
            services = yield getPage(base_url + '/getAgentStatus',
                       headers={"content-type": "application/json", "Authorization": authHeader}
                       )
            services = json.loads(services)
            results['services'] = services['services']['agents']
        except Exception, e:
            log.error("%s: %s", device.id, e)
            returnValue(None)
        
        log.info("Peregrine Services: %s\n" % str(services))
        
        rm = self.relMap()
        
        # Process services
        for service in results['services']:
            rm.append(self.objectMap({
                'id' : prepId(service['ip']),
                'title' : service['ip'],
                'status' : service['status'],
                }))
                                                                                                            
        
        returnValue(rm)
    
    def process(self, device, results, log):
        """ Process results. Return iterable of datamaps or None."""
        return results
