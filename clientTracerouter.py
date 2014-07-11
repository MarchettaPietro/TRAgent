#!/usr/bin/env python

# ===================================================================
# @(#)Traceroute Platform PROJECT
# @(#)clientTracerouters.py
#
# @author Pietro Marchetta
#               (pietro.marchetta@unina.it)
# @date  7/2014
# ===================================================================

"""
XML-RPC interface for a Planetlab Tracerouter 
"""


from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import threading
import json
import socket
import sys
import socket
import logging
import logging.config
import Queue
import SocketServer
import base64
import sqlite3
import cPickle

# si basa su un database sqlite in cui memorizza tutti i risultati delle analisi: una tabella id misura, status, risultato, json risultato, raw result
# usa l'approccio sottometti e ritorna dopo 



class MultithreadedXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer): 
	"""Create a Multithreaded SimpleXMLRPCServer"""	
	def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler, \
		logRequests=True, encoding=None, bind_and_activate=True, \
		address_family=socket.AF_INET, auth_map=None):
	
		self.auth_map = auth_map
		SimpleXMLRPCServer.__init__(self, addr=addr, requestHandler=requestHandler, logRequests=logRequests, 
			encoding=encoding, bind_and_activate=bind_and_activate)
        
        #SimpleJSONRPCServer.__init__(self, addr, requestHandler, logRequests,
                                     #encoding, bind_and_activate, address_family)
                                     
    
class SecuredHandler(SimpleXMLRPCRequestHandler):
	"""Customization of SimpleXMLRPCRequestHandler to employ basic HTTP Authorization"""
	rpc_paths = ('/RPC2',)
	
	def __init__(self, request, client_address, server, client_digest=None):
		self.__logger = logging.getLogger(__name__)
		self.auth_map = server.auth_map
		SimpleXMLRPCRequestHandler.__init__(self, request, client_address, server)
		self.client_digest = client_digest
			

	def do_POST(self):
	
		if self.auth_map != None:
			if self.headers.has_key('authorization') and self.headers['authorization'].startswith('Basic '):
				authenticationString = base64.b64decode(self.headers['authorization'].split(' ')[1])
				if authenticationString.find(':') != -1:
					username, password = authenticationString.split(':', 1)
					self.__logger.info('Got request from %s:%s' % (username, password))
	
					if self.auth_map.has_key(username) and self.verifyPassword(username, password):
						return SimpleXMLRPCRequestHandler.do_POST(self)
					else:
						self.__logger.error('Authentication failed for %s:%s' % (username, password))
			
			self.__logger.error('Authentication failed')
			self.send_response(401)
			self.end_headers()
			return False
	
		return SimpleXMLRPCRequestHandler.do_POST(self)
    
	def verifyPassword(self, username, givenPassword):
		return self.auth_map[username] == givenPassword



class Tracerouter(object):
		"""Server Thread managing incoming XMLRPC requests for path to traceroute"""

		def __init__(self, auth_map, common, logger):
			self.__logger = logger
			self.auth_map = auth_map
			self.__common = common
			self.__requests = Queue.Queue(0)
			
			self.__mutex = threading.Lock()
			
			#check if database exists
			if not self.databaseExists():
				
				#crea database if not exists
				conn = sqlite3.connect(self.__common['db.path'])
				c = conn.cursor()				
				#crea table #id misura che e' row_id non va specificato, status, errors, json risultato, raw result
				c.execute('''CREATE TABLE traceroutes (mid integer primary key autoincrement, status text, target text, errors text, json text, raw text)''')
				conn.commit()
				conn.close()

				
		def databaseExists(self):
			""" check if db.path exists """
			from os.path import isfile, getsize
			
			if not isfile(self.__common["db.path"]):
				return False

			if getsize(self.__common["db.path"]) < 100: # SQLite database file header is 100 bytes
				return False
			else:
				fd = open(self.__common["db.path"], 'rb')
				Header = fd.read(100)
				fd.close()
			
			if Header[0:16] == 'SQLite format 3\000':
				return True
			else:
				return False
		
			
		
		def submit(self, query):
			""" create a new row in the database, create a new request (json object), put the new request in the queue shared with the workers  """
			
			self.loginfo(">> "+query)			
			
			#create a new request
			request = {'status':"ongoing", 'target':query.strip(), 'hops':[], 'errors':[], 'id':-1}
			
			self.loginfo(str(request))			
			conn = None
			
			#check on request target (valid IP address)
			try:
				socket.inet_aton(request['target']) 
			except:
				request['errors'].append('Not valid Target')
				request['status'] = 'failed'
		
		
			#store in db
			self.__mutex.acquire()
			try:
				#create a new row and take the id		
				conn = sqlite3.connect(self.__common["db.path"])
				cc = conn.cursor()

				#pdata = cPickle.dumps(request, cPickle.HIGHEST_PROTOCOL)
				cc.execute('INSERT INTO traceroutes (status,target, errors,json,raw) VALUES (?,?,?,?,?)', (request['status'],request['target'],"|".join(request['errors']), json.dumps(request), ''))
				if request['status'] != "failed":
					request['id'] = cc.lastrowid
					self.__requests.put(request)			
					
				conn.commit()

			except Exception, ee:
				request['status'] != "failed"
				request['errors'].append(str(ee))
				self.logerror("Failure: "+json.dumps(request))
				request['id'] = -1
				
			finally:
				if conn:
					conn.close()
				self.__mutex.release()

			self.logdebug(str(request))
			return request['id']
			
		
		def status(self, m_id):
						
			self.loginfo("Requested status of ("+str(m_id)+")")
			conn = None
			cc = None
			
			res = {'status':'', 'errors':[]}

			try:
				conn = sqlite3.connect(self.__common["db.path"])
				cc = conn.cursor()
				cc.execute('SELECT status FROM traceroutes WHERE rowid=:rowid', {'rowid':m_id})
				res['status'] = cur.fetchone()
			
			except Exception, ee:
				logerror("Status Error:")
				res['errors'].append(str(ee))

			finally:
				if cc:
					cc.close()
					
				if conn:
					conn.close()
				
			return res
				
		
		def results(self, m_id):
			
			self.loginfo("Requested results for ("+str(m_id)+")")
			
			conn = None
			cc = None
			
			res = {'result':'', 'errors':[]}

			try:
				conn = sqlite3.connect(self.__common["db.path"])
				cc = conn.cursor()
				cc.execute('SELECT json FROM traceroutes WHERE rowid=%s', m_id)
				res['result'] = cur.fetchone()
			
			except Exception, ee:
				self.logerror("Results Error:")
				res['errors'].append(str(ee))

			finally:
				if cc:
					cc.close()
					
				if conn:
					conn.close()
				
			return res
			
		def loginfo(self, text):
			self.__logger.info("[Main] " +text)
		
		def logerror(self, text):
			self.__logger.error("[Main] " +text, exc_info = True)
			
		def logwarn(self, text):
			self.__logger.warning("[Main] " +text)

		def logdebug(self, text):
			self.__logger.debug("[Main] " +text)			
		

		def run(self):

			server = MultithreadedXMLRPCServer((self.__common["querier.binding.host"], int(self.__common["querier.binding.port"])), requestHandler=SecuredHandler, logRequests=True, auth_map=self.auth_map)
						
			server.register_function(self.submit, 'submit')
			server.register_function(self.status, 'status')			
			server.register_function(self.results, 'results')
			
			self.loginfo('Starting service on port: %d' % int(self.__common["querier.binding.port"]))

			try:
				server.serve_forever()				
			except KeyboardInterrupt:
				self.loginfo('Quitting..')
			
			
def load_auth(auth_file):
	""" Load authorization file """
	auth_map = {}
	
	with open(auth_file) as f:
		for line in f:
			if len(line.strip())==0 or line.startswith("#"):
				continue				
			(user, password) = line.strip().split(':')
			auth_map[user] = password
	
	return auth_map


def load_config(conf_file):
	""" Load configuration file """
	params = {}
	lines = open(conf_file).readlines()
	for ll in lines:
		if len(ll.strip())==0 or ll.startswith("#"):
			continue
			
		params[ll.split("=")[0]]=ll.split("=")[1].strip()
	
	return params
			
   
if __name__ == '__main__':
    
	if len(sys.argv) != 3:
		sys.stderr.write('Usage: <config file> <auth_file>\n')
		sys.exit(1)
	
	conf_file = sys.argv[1]
	auth_file = sys.argv[2]
	auth_map = load_auth(auth_file)
	common = load_config(conf_file)
	
	#Logger
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(formatter)
	#logger.addHandler(consoleHandler)
	handler = logging.FileHandler(filename=common["log.file"])
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	
	service = Tracerouter(auth_map, common, logger)
	service.run()
	
