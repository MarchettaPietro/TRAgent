# ===================================================================
# @(#)TRAgent  PROJECT
# @(#)DBManager.py
#
# @author Pietro Marchetta
#               (pietro.marchetta@unina.it)
# @date  16/12/2013
# ===================================================================

import MySQLdb as mdb

class DBManager():	
	
	def __init__(self,  common):
			
		self.__common = common
				
		self.__con = mdb.connect(self.__common["db.host"], self.__common["db.user"], self.__common["db.password"], self.__common["db.db"]);			
		self.__con.autocommit(True)
			
		self.__stop = False	
		self.complete = False


	def execute(self, sql):
		"""Execute sql statement on database"""
		
		self.__cur = self.__con.cursor()
		self.__cur.execute(sql)
		
		return self.__cur
		
	def get_connection(self):
		return self.__con
		
	
	def close(self):
		"""Close all the connection to the database"""
			
		if self.__con:
			self.__con.close()
		

