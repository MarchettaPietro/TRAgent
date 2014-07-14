#!/usr/bin/env python

#pietro.marchetta@unina.it

import sys
import xmlrpclib
import time
import sqlite3

if __name__ == "__main__":	


	usages = "usage: %prog  <db> <nodes success> <node details>"  

	if len(sys.argv) != 4:
		sys.stderr.write(usages)
		sys.exit(1)
	
	nodes_success = [x.strip() for x in open(sys.argv[2]) if len(x.strip())!=0]
	
	node2as = {}	
	for ll in open(sys.argv[3]):
		vp, asn = ll.split()
		node2as[vp] = asn
		
	
	cc = None
	conn = None

	try:
		
		conn = sqlite3.connect(sys.argv[1])
		cc = conn.cursor()			
		for nn in node2as:
			if nn in nodes_success:
				cc.execute("""INSERT OR REPLACE INTO vps(vp,asn,active) VALUES(?,?,1)""", (nn,node2as[nn]))
			else:
				cc.execute("""INSERT OR REPLACE INTO vps(vp,asn,active) VALUES(?,?,0)""", (nn,node2as[nn]))

		conn.commit()
		
	except Exception, ee:
		sys.stderr.write("Error: "+str(ee))

	finally:
		if cc:
			cc.close()
			
		if conn:
			conn.close()		
	
