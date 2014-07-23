# ===================================================================
# @(#)TRAgent PROJECT
#
# @author Pietro Marchetta
#               (pietro.marchetta@unina.it)
# @date  15/07/2014
# ===================================================================


import threading
import time
import Queue
from TracerouteManager import TracerouteManager
#from traceMapper import Mapper

"""
Dispatcher is in charge of creating a new TracerouteManager for the incoming requests
"""


class Dispatcher(threading.Thread):	
	
	def __init__(self, incoming_requests, logger, common):
		super(Dispatcher, self).__init__()
		
		self.__common = common
		self.__incoming_requests = incoming_requests #queue for requests
		self.__tpool = [] #list of TracerouteManager threads		
		
		self.__stop = False
		
		self.__logger = logger 
		self.loginfo("Started.")
		

	def loginfo(self, text):
		self.__logger.info("[Dispatcher] " +text)
	
	def logerror(self, text):
		self.__logger.error("[Dispatcher] " +text)
		
	def logwarn(self, text):
		self.__logger.warning("[Dispatcher] " +text)

	
	def __clean_tpool(self):
		""" Remove dead threads """
		#self.loginfo("Removing dead thread from tpool")
		toremove = []
		for tt in self.__tpool:
			if not tt.isAlive():
				toremove.append(tt)
		for tt in toremove:
			self.__tpool.remove(tt)


	def __close_all_tpool(self):
		""" Stop and join threads """
		self.loginfo(" Closing all.")
		self.__clean_tpool()
		
		for tt in self.__tpool:
			tt.stopme()
		
		for tt in self.__tpool:
			while tt.isAlive():
				tt.join(5)
				self.loginfo(" Still to close: "+str(len(self.__tpool)))


	def stopme(self):
		self.loginfo("Stopping.")
		self.__stop = True
		self.__close_all_tpool()
		

	def run (self):
		self.loginfo("Running ")
		
		while not self.__stop:	
			try:
				in_request = self.__incoming_requests.get(True, 1)				
			except Queue.Empty:
				#self.loginfo("No incoming request ")
				#self.loginfo("Active threads: "+str(len(self.__tpool)))
				#self.loginfo("Stop flag: "+str(self.__stop))
				self.__clean_tpool()
				continue
			
			self.loginfo("Launching TracerouteManager on "+str(in_request))

			tt = TracerouteManager(in_request, self.__logger, self.__common)
			tt.start()
			self.__tpool.append(tt)		

		self.stopme()
						
