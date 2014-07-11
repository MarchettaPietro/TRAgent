#!/usr/bin/env python

import xmlrpclib
import time
import ast
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
		print id
		sys.exit(1)
		
	status = ['ongoing']
	
	print "%s %s"%("#Status", "Process")
	while status[0] == ['ongoing']:
		status = s.status(id)
		print status
		time.sleep(10)

	print status
	#if status[0]=="FINISHED":
	res = s.results(id)
	dic = ast.literal_eval(res[0])
	pprint.pprint(dic)
	


