#!/usr/bin/env python

import xmlrpclib
import time
import ast
import json
import pprint

from optparse import OptionParser
import xmlrpclib,sys

if __name__ == "__main__":	

	#usages = "usage: %prog  <File containing the query>" 
	#parser = OptionParser(usage=usages) 
	#(options, args) = parser.parse_args()

	#if not len(args)==1:  
	   #parser.print_help()
	   #sys.exit(0)
	
	#with open(args[0], 'r') as content_file:
		#query = content_file.read()
	
	#s = xmlrpclib.ServerProxy('http://parruccone75:patriziaasparago@sim15.usc.edu:64751')
	s = xmlrpclib.Server('http://parruccone75:patriziaasparago@143.225.229.127:64751')
	#s = xmlrpclib.Server('http://parruccone75:patriziaasparago@10.0.3.15:64751')
	
	res = s.active()
	print res,len(res['result'])
	
	res = s.active(150)
	print res,len(res['result'])
	
	res = s.active(680)
	print res,len(res['result'])
	
	res = s.ases()
	print res,len(res['result'])
	
	raw_input()

	#id =  s.submit('host2.planetlab.informatik.tu-darmstadt.de','143.225.229.127')
	##id =  s.submit('143.225.229.127','149.3.176.25')
	#if id<0:
		#print "Obtained measurement ID: ", id
		#sys.exit(1)
		
	#res = {'status':['ongoing'], 'erros':[]}
	
	#print "%s"%("#Status")
	#while res["status"][0] != "success" and res["status"][0] != "failed":
		#res = s.status(id)
		#print res
		#time.sleep(2)

	##print res
	#if res["status"][0] == "success":
		#res = s.results(id)
		#print res
		#dd = json.loads(res['result'][0])
		#pprint.pprint(dd)
		
		###dic = ast.literal_eval(res['result'])
		###pprint.pprint(dic)
		

	#raw_input()

	id =  s.submit('planetlab1.cs.du.edu','143.225.229.127')
	#id =  s.submit('143.225.229.127','149.3.176.25')
	if id<0:
		print "Obtained measurement ID: ", id
		sys.exit(1)
		
	res = {'status':['ongoing'], 'erros':[]}
	
	print "%s"%("#Status")
	while res["status"][0] != "success" and res["status"][0] != "failed":
		res = s.status(id)
		print res
		time.sleep(2)

	#print res
	if res["status"][0] == "success":
		res = s.results(id)
		print res
		dd = json.loads(res['result'][0])
		pprint.pprint(dd)
		
		##dic = ast.literal_eval(res['result'])
		##pprint.pprint(dic)
