#!/usr/bin/env python

import xmlrpclib
import time
import ast
import json
import pprint

from optparse import OptionParser
import xmlrpclib,sys

if __name__ == "__main__":	

	usages = "usage: %prog  <File containing the query>" 
	parser = OptionParser(usage=usages) 
	(options, args) = parser.parse_args()

	if not len(args)==1:  
	   parser.print_help()
	   sys.exit(0)

	with open(args[0], 'r') as content_file:
		query = content_file.read()
	
	#s = xmlrpclib.ServerProxy('http://parruccone75:patriziaasparago@sim15.usc.edu:64751')
	#s = xmlrpclib.Server('http://parruccone75:patriziaasparago@localhost:64751')
	s = xmlrpclib.Server('http://parruccone75:patriziaasparago@localhost:64751')
	
	id =  s.submit(query)
	if id<0:
		print "Obtained measurement ID: ", id
		sys.exit(1)
		
	res = {'status':['ongoing'], 'erros':[]}
	
	print "%s"%("#Status")
	#while status[0] == ['ongoing']:
	while res["status"][0] != "success" and res["status"][0] != "failed":
		res = s.status(id)
		print res
		time.sleep(2)

	print res
	if res["status"][0] == "success":
		res = s.results(id)
		print res
		dd = json.loads(res['result'][0])
		pprint.pprint(dd)
		
		#dic = ast.literal_eval(res['result'])
		#pprint.pprint(dic)
		


