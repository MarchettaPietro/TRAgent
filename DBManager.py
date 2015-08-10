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
		self.__con = None
		self.__stop = False	
		self.complete = False
		
		self.connect()

	def connect(self)
		self.__con = mdb.connect(self.__common["db.host"], self.__common["db.user"], self.__common["db.password"], self.__common["db.db"]);			
		self.__con.autocommit(True)
	
	
	def execute(self, sql):
		"""Execute sql statement on database"""

		try:
		  cursor = self.__con.cursor()
		  cursor.execute(sql)
		except (AttributeError, MySQLdb.OperationalError):
		  self.connect()
		  cursor = self.__con.cursor()
		  cursor.execute(sql)
		return cursor

				
	def get_connection(self):
		return self.__con
		
	
	def close(self):
		"""Close all the connection to the database"""
			
		if self.__con:
			self.__con.close()
		


