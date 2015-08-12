#!/usr/bin/env python
# ===================================================================
# @(#)TRAgent PROJECT
#
# @author Pietro Marchetta
# (pietro.marchetta@unina.it)
# @date  15/07/2014
# ===================================================================

import threading
import time
import json
import re
import pexpect
import sys
import logging

from DBManager import DBManager

""" Launch and parse traceroutes from planetlab nodes through an ssh connection """

#FROM THIS:

##[uninaonelab_merlin@host2 ~]$ sudo traceroute -n 143.225.229.127
#traceroute to 143.225.229.127 (143.225.229.127), 30 hops max, 60 byte packets
#1  130.83.166.241  0.303 ms  0.377 ms  0.370 ms
#2  130.83.164.250  0.664 ms  0.659 ms  0.881 ms
#3  130.83.253.250  0.617 ms  0.614 ms  0.608 ms
#4  130.83.254.13  0.848 ms  0.849 ms  1.078 ms
#5  82.195.78.50  0.575 ms  0.571 ms  0.566 ms
#6  82.195.78.41  0.789 ms  0.516 ms  0.495 ms
#7  82.195.67.213  1.179 ms  1.024 ms  1.002 ms
#8  213.248.76.101  2.462 ms  2.459 ms  2.454 ms
#9  62.115.137.182  19.587 ms  19.573 ms  19.567 ms
#10  213.155.135.13  1.565 ms 80.91.246.105  1.542 ms  1.529 ms
#11  130.117.14.89  2.742 ms  2.087 ms  2.730 ms
#12  130.117.48.114  2.793 ms  2.281 ms 130.117.48.70  3.395 ms
#13  154.54.38.50  7.995 ms 154.54.38.58  8.077 ms 154.54.38.50  7.768 ms
#14  130.117.0.250  13.149 ms  13.153 ms 130.117.3.114  13.128 ms
#15  154.54.62.9  16.646 ms 130.117.48.158  16.766 ms 154.54.62.9  16.545 ms
#16  130.117.1.130  27.782 ms  27.926 ms 130.117.1.126  27.914 ms
#17  149.6.22.74  27.810 ms  27.793 ms  27.753 ms
#18  90.147.80.54  29.360 ms 90.147.80.58  39.861 ms 90.147.80.1  38.172 ms
#19  90.147.80.113  23.457 ms 90.147.80.166  44.380 ms  44.368 ms
#20  90.147.80.170  29.062 ms 90.147.80.150  40.532 ms 90.147.80.170  29.138 ms
#21  193.206.130.10  43.510 ms  43.470 ms  41.196 ms
#22  143.225.190.97  75.774 ms  74.724 ms  70.140 ms
#23  143.225.229.127  29.872 ms  37.593 ms  29.999 ms

class TracerouteManager(threading.Thread):
    def __init__(self, request, logger, common):
        super(TracerouteManager, self).__init__()
        self.__request = request  #json request
        self.__raw = ''  #raw result for traceroute
        self.__logger = logger
        self.__common = common
        self.__dbmanager = DBManager(self.__common)

        self.__stop = False

        self.loginfo("Traceroute Manager for " + str(self.__request) + "  started.")


    def loginfo(self, text):
        self.__logger.info("[TRManager][" + str(self.__request["target"]) + "] " + text)

    def logerror(self, text):
        self.__logger.error("[TRManager][" + str(self.__request["target"]) + "] " + text, exc_info=True)

    def logwarn(self, text):
        self.__logger.warning("[TRManager][" + str(self.__request["target"]) + "] " + text)

    def logdebug(self, text):
        self.__logger.debug("[TRManager][" + str(self.__request["target"]) + "] " + text)

    def stopme(self):
        self.loginfo("Stopping.")
        self.__stop = True

    def remove_node(self, vp):
        """ set as unactive a node in case of failure """

        cc = None
        sql = "UPDATE vps SET fails=fails+1 WHERE vp='%s'" % (vp)
        self.logdebug(sql)

        try:
            cc = self.__dbmanager.execute(sql)

        except Exception, ee:
            self.__request['status'] != "failed"
            self.__request['errors'].append(str(ee))
            self.logerror("Failure: " + json.dumps(self.__request))

        finally:
            if cc:
                cc.close()


    def reset_node(self, vp):
        """ set as unactive a node in case of failure """

        cc = None
        sql = "UPDATE vps SET fails=0 WHERE vp='%s'" % (vp)
        self.logdebug(sql)

        try:
            cc = self.__dbmanager.execute(sql)

        except Exception, ee:
            self.__request['status'] != "failed"
            self.__request['errors'].append(str(ee))
            self.logerror("Failure: " + json.dumps(self.__request))

        finally:
            if cc:
                cc.close()


    def update_db(self):
        """Update destination request in db"""
		
        self.__raw = self.__raw.replace('\'', '')		
		
        cc = None
        sql = "UPDATE traceroutes SET status='%s', errors='%s', json='%s', raw='%s' WHERE mid=%s" % (
            self.__request['status'], " ".join(self.__request['errors']), json.dumps(self.__request), self.__raw,
            self.__request["id"])
        #sql = "UPDATE traceroutes SET status='%s', errors='%s', json=`%s`, raw=`%s` WHERE mid=%s"%(self.__request['status']," ".join(self.__request['errors']), "", self.__raw, self.__request["id"])
        self.logdebug(sql)

        try:
            cc = self.__dbmanager.execute(sql)

        except Exception, ee:
            self.__request['status'] != "failed"
            self.__request['errors'].append(str(ee))
            self.logerror("Failure: " + json.dumps(self.__request))

        finally:
            if cc:
                cc.close()


    def parser_tr_output(self, tr_output):
        """Parser for the traceroute output"""

        tr_lines = tr_output.split("\n")  #One IP per hop
        tr_final = []

        for ll in tr_lines:
            if "traceroute" in ll or len(ll) == 0:
                continue
            try:
                int(ll.split()[0])  # no starting ttl on the line
            except:
                continue

            ips = re.findall(r'[0-9]+(?:\.[0-9]+){3}', ll)
            if len(ips) == 0:
                tr_final.append("0.0.0.0")
            else:
                tr_final.append(ips[0])

        return tr_final


    def run(self):
        """Launch remotely a classic traceroute toward the destination """

        self.loginfo("Tracerouting")
        child = None
        self.__request["status"] = "ongoing"
        try:
            #child = pexpect.spawn("sudo traceroute -f "+self.__common["first_ttl"]+ " -m "+self.__common["max_ttl"]+ " -n "+self.__request["target"])
            cmd = "ssh -o StrictHostKeyChecking=no -i " + self.__common['key'] + " -tt -l " + self.__common[
                "remotel"] + " " + self.__request['vp'] + " \"traceroute -n " + self.__request["target"] + " \" "
            self.loginfo(cmd)

            child = pexpect.spawn(cmd)
            ris = child.expect([pexpect.EOF, "\$"], timeout=int(self.__common["timeout"]))
            tr_output = child.before

            self.__raw = tr_output
            self.__raw.replace('\'', '')

            self.loginfo("Parsing")
            tr_final = self.parser_tr_output(self.__raw)

            self.__request["hops"] = tr_final

            if len(self.__request["hops"]) == 0:
                raise Exception("No Trace")
            else:
                self.__request["status"] = 'success'

            self.loginfo("Updating")
            self.update_db()
            self.reset_node(self.__request['vp'])

        except Exception, ee:
            self.__request['status'] = "failed"
            self.__request['errors'].append('Timeout Exceeded')
            self.logerror("Failure: " + json.dumps(self.__request))
            self.remove_node(self.__request['vp'])
            self.update_db()

        finally:

            if child:
                child.terminate(force=True)
                child.close()

        #closing DBManager
        self.__dbmanager.close()

        self.loginfo("Quitting")


def load_config(conf_file):
    """ Load configuration file """
    params = {}
    lines = open(conf_file).readlines()
    for ll in lines:
        if len(ll.strip()) == 0 or ll.startswith("#"):
            continue

        params[ll.split("=")[0]] = ll.split("=")[1].strip()

    return params


if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: <config file>\n')
        sys.exit(1)

    conf_file = sys.argv[1]
    common = load_config(conf_file)

    #Logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s]%(message)s')
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    #logger.addHandler(consoleHandler)
    handler = logging.FileHandler(filename=common["log.file"])
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    request = {'status': "ongoing", 'target': "143.225.229.127", 'errors': [], 'id': 11,
               'vp': 'host2.planetlab.informatik.tu-darmstadt.de'}

    dbmanager = DBManager(common)
    sql = "INSERT INTO traceroutes (status, vp, target, errors,json,raw) VALUES (%s,%s,%s,%s,%s)" % (
        request['status'], request["vp"], request['target'], "|".join(request['errors']), json.dumps(request), '')

    cc = None
    try:

        cc = db.manager(sql)
        if request['status'] != "failed":
            request['id'] = cc.lastrowid

    except Exception, ee:
        request['status'] != "failed"
        request['errors'].append(str(ee))
        request['id'] = -1

    finally:
        if cc:
            cc.close()

    if request['status'] != "failed":
        tt = TracerouteManager(request, logger, common)
        tt.start()

        while tt.isAlive():
            tt.join(timeout=5)
			


