#TRAgent
=======

A measurement engine to launch traceroutes from planetlab nodes wrapped in an XML-RPC interface.


## Functionality
- launch, parse and store a traceroute from a given planetlab node toward a given destination
- automatic plugging of all the planetlb nodes able to issue traceroutes

## Available methods

`res = ases()`

- res (dictionary): a dictionary containing the following keywords		    		
  - code(integer): syntetic returned code (higher than 0 for no errors)
  - errors(list): array of errors encountered
  - result(list): a list of ASes where active planetlab nodes are located.



`res = active(asn=None)`

- asn (integer): an autonomous system number
- res (dictionary): a dictionary containing the following keywords		    		
  - code(integer): syntetic returned code (higher than 0 for no errors)
  - errors(list): array of errors encountered
  - result(list): a list of tuples (active planetlab node, asn). If asn is specified, it returns a list of active planetlab nodes within the AS #asn.


		
`measurement_id = submit(node,destination)`

- node(String) - a planetlab node identifier (typically, its hostname)
- destination(String) - IP address of the targeted destination
- measurement_id (integer): an id which can be used to retrieve status and results of traceroutes




`res = status(measuremet_id)`

- measurement_id (integer): an identifier for a measurement
- res (dictionary): a dictionary containing the following keywords		    		
  - code(integer): syntetic returned code (higher than 0 for no errors)
  - errors(list): array of errors encountered
  - status(string): ongoing/success/failed



`res = results(measuremet_id)`

- measurement_id (integer): an identifier for a measurement
- res (dictionary): a dictionary containing the following keywords		    		
  - code: syntetic returned code (higher than 0 for no errors)
  - errors: array of errors encountered
  - result: json object returning details about the performed measurement. An example is reported in the following:

                `{u'errors': [],
            			 u'hops': [u'130.253.21.126',
            			           u'130.253.101.14',
            			           u'129.19.165.1',
            			           u'192.43.217.222',
            			           u'198.71.45.57',
            			           u'62.40.125.17',
            			           u'62.40.98.108',
            			           u'62.40.98.113',
            			           u'62.40.125.181',
            			           u'90.147.80.70',
            			           u'90.147.80.102',
            			           u'90.147.80.106',
            			           u'90.147.80.150',
            			           u'143.225.190.97',
            			           u'143.225.190.97'],
            			 u'id': 13,
            			 u'status': u'success',
            			 u'target': u'143.225.229.127',
            			 u'vp': u'planetlab1.cs.du.edu'}`

