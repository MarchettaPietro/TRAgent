#!/usr/bin/env python

# ===================================================================
# @(#)TRAgent PROJECT
#
# @author Pietro Marchetta
#               (pietro.marchetta@unina.it)
# @date  15/07/2014
# ===================================================================


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
	#s = xmlrpclib.Server('http://parruccone75:patriziaasparago@143.225.229.127:64751')
	s = xmlrpclib.Server('http://parruccone75:patriziaasparago@127.0.0.1:64751')
	#s = xmlrpclib.Server('http://parruccone75:patriziaasparago@10.0.3.15:64751')
	
	print "\n\nACTIVE"
	res = s.active()
	print res,len(res['result'])
	
	print "\n\nACTIVE(150)"
	res = s.active(150)
	print res,len(res['result'])
	
	print "\n\nACTIVE(680)"
	res = s.active(680)
	print res,len(res['result'])
	
	print "\n\ASES"
	res = s.ases()
	print res,len(res['result'])
	


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
	
	ids = []
	print "\n\ns.submit('planetlab1.cs.du.edu','143.225.229.127')"
	ids.append(s.submit('planetlab1.cs.du.edu','143.225.229.127'))
	print ids
	
	print "\n\ns.submit('dschinni.planetlab.extranet.uni-passau.de','143.225.229.127')"
	ids.append(s.submit('dschinni.planetlab.extranet.uni-passau.de','143.225.229.127'))
	print ids
		
	print "\n\ns.submit('planetlab02.tkn.tu-berlin.de','143.225.229.127')"
	ids.append(s.submit('planetlab02.tkn.tu-berlin.de','143.225.229.127'))
	print ids
		
	print "\n\ns.submit('aladdin.planetlab.extranet.uni-passau.de','143.225.229.127')"
	ids.append(s.submit('aladdin.planetlab.extranet.uni-passau.de','143.225.229.127'))
	print ids
	
	print "\n\ns.submit('planetlab1.informatik.uni-goettingen.de','143.225.229.127')"
	ids.append(s.submit('planetlab1.informatik.uni-goettingen.de','143.225.229.127'))
	print ids	
	
	#id =  s.submit('143.225.229.127','149.3.176.25')
	if not True in [x>0 for x in ids]:
		print "Problems: ", ids
		sys.exit(1)
		
	while len(ids)>0:
		for ii in ids:
			cres = s.status(ii)
			
			if cres<0:
				print ii,cres
				ids.remove(ii)
			
			else:
				if cres["status"]=="success":
					nres = s.results(ii)
					print nres
					dd = json.loads(nres['result'][0])
					pprint.pprint(dd)
					ids.remove(ii)
		
		time.sleep(10)
				
		
	
	#res = {'status':['ongoing'], 'erros':[]}
	
	#print "%s"%("#Status")
	#while res["status"] != "success" and res["status"] != "failed":
		#res = s.status(id)
		#print res
		#time.sleep(5)

	##print res
	#if res["status"] == "success":
		#res = s.results(id)
		#print res
		#dd = json.loads(res['result'][0])
		#pprint.pprint(dd)
		
		###dic = ast.literal_eval(res['result'])
		###pprint.pprint(dic)
