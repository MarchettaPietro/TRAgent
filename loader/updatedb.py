#!/usr/bin/env python

#pietro.marchetta@unina.it

import sys
import MySQLdb as mdb

def load_config(conf_file):
	""" Load configuration file """
	params = {}
	lines = open(conf_file).readlines()
	for ll in lines:
		if len(ll.strip())==0 or ll.startswith("#"):
			continue
			
		params[ll.split("=")[0]]=ll.split("=")[1].strip()
	
	return params


if __name__ == "__main__":	


	usages = "usage: %prog  <config.ini> <nodes success> <node details>"  

	if len(sys.argv) != 4:
		sys.stderr.write(usages)
		sys.exit(1)
	
	nodes_success = [x.strip() for x in open(sys.argv[2]) if len(x.strip())!=0]
	
	common = load_config(sys.argv[1])

	node2as = {}	
	for ll in open(sys.argv[3]):
		vp, asn = ll.split()
		try:
			int(asn)
		except:
			continue
			
		node2as[vp] = asn

	conn = mdb.connect(common["db.host"], common["db.user"], common["db.password"], common["db.db"]);					
	cur = conn.cursor()
	conn.autocommit(True)
	
	#create tables if not exist
	sql = 'CREATE TABLE IF NOT EXISTS vps (vp varchar(200) not null, asn int, active int,  primary key(vp) )'
	cur.execute(sql)
	
	sql = 'CREATE TABLE IF NOT EXISTS traceroutes (mid int auto_increment, status text, vp text, target text, errors text, json text, raw text, primary key (mid))'
	cur.execute(sql)
	
	for nn in node2as:
		if nn in nodes_success:
			sql = "REPLACE INTO vps(vp,asn,active) VALUES('%s',%s,1)"%(nn, node2as[nn])
		else:
			sql = "REPLACE INTO vps(vp,asn,active) VALUES('%s',%s,0)"%(nn, node2as[nn])
		
		#print sql
		cur.execute(sql)
		
	cur.close()
	conn.close()
	
