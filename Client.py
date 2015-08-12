#!/usr/bin/env python

# ===================================================================
# @(#)TRAgent PROJECT
#
# @author Pietro Marchetta
#               (pietro.marchetta@unina.it)
# @date  15/07/2014
# ===================================================================


import xmlrpclib
#import jsonrpclib
import time
import ast
import json
import pprint

from optparse import OptionParser
import sys

if __name__ == "__main__":	

	s = xmlrpclib.ServerProxy('http://parruccone75:patriziaasparago@143.225.229.145:64751/RPC2')
	#s = jsonrpclib.Server('http://parruccone75:patriziaasparago@143.225.229.145:64751')
	
	try:
		res = s.active()
		print res,len(res['result'])
	
	except xmlrpclib.Fault as err:
		print "A fault occurred"
		print "Fault code: %d" % err.faultCode
		print "Fault string: %s" % err.faultString
	except xmlrpclib.ProtocolError as err:
		print "A protocol error occurred"
		print "URL: %s" % err.url
		print "HTTP/HTTPS headers: %s" % err.headers
		print "Error code: %d" % err.errcode
		print "Error message: %s" % err.errmsg
    
	
	#res = s.active(150)
	#print res,len(res['result'])
	
	#res = s.active(680)
	#print res,len(res['result'])
	
	#res = s.ases()
	#print res,len(res['result'])
	
	#raw_input()

	id =  s.submit('planetlab1.cs.du.edu','143.225.229.127')
	if id<0:
		print "Obtained measurement ID: ", id
		sys.exit(1)
		
	res = {'status':['ongoing'], 'erros':[]}
	
	print "%s"%("#Status")
	while res["status"] != "success" and res["status"] != "failed":
		res = s.status(id)
		print res
		time.sleep(2)

	#print res
	if res["status"] == "success":
		res = s.results(id)
		print res
		
		##dic = ast.literal_eval(res['result'])
		##pprint.pprint(dic)
