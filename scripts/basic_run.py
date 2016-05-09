#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, time
import subprocess as sp
from threading import Thread

HOMEDIR = '/home/gticn/'
BASEDIR = HOMEDIR+'workspace/'
CLASSDIR = BASEDIR+'prodcon/bin'
MAINCLASS = 'prodcon/BasicExperiment'
CPDIR = BASEDIR+'prodcon/lib'
FILEPREFIX = 'ccnx:/rnp.br'
JAVARGS = '-Xmx1600M'
CONFFILE = HOMEDIR+'experiment.conf'

class StreamClient(Thread):
   def __init__(self, name, runnumber, starttime):
      Thread.__init__(self)
      self.name = name
      self.runnumber = runnumber
      self.starttime = starttime
      self.classdir = ""
      self.mainclass = ""
      self.parameters = ""
      self.jardir = ""
      return
   def run(self):
      print "Running client %s-%s..."%(self.name, self.runnumber)
      cmd = "java %s -cp %s %s %s"%(JAVARGS, self.gencp(), self.mainclass, self.parameters)
      print cmd
      stdoutarq = open("out-%s-%s.txt"%(self.name, self.runnumber), 'w')
      stderrarq = open("err-%s-%s.txt"%(self.name, self.runnumber), 'w')
      waittime = self.starttime - int(time.time())
      if waittime > 0:
         print "Awaiting %ld seconds..."%waittime
         time.sleep(waittime)
      ret = sp.call(cmd, shell=True, stdout=stdoutarq, stderr=stderrarq)
      stdoutarq.close()
      stderrarq.close()
      if ret != 0:
         print 'Process %s-%s return value: %d\n'%(self.name, self.runnumber, ret)
      return
   def setcp(self, jardir):
      if jardir[-1] == '/':
         self.jardir = jardir[:-1]
      else:
         self.jardir = jardir
      return
   def setparameters(self, parms):
      self.parameters = parms
      return
   def setclassdir(self, classdir, mainclass):
      self.classdir = classdir
      self.mainclass = mainclass
   def gencp(self):
      rescp = ""
      for item in os.listdir(self.jardir):
         if item[-4:] == '.jar':
            rescp += '%s/%s:'%(self.jardir, item)
      rescp += self.classdir
      return rescp

class Main:
   def __init__(self):
      pass
   def main(self):
      basename = sys.argv[1]
      runnumber = int(sys.argv[2])
      launchtime = long(sys.argv[3])
      sc = StreamClient(basename, runnumber, launchtime)
      sc.setclassdir(CLASSDIR, MAINCLASS)
      sc.setcp(CPDIR)
      sc.setparameters(CONFFILE)
      sc.start()
      sc.join()
      return

if __name__ == '__main__':
   m = Main()
   m.main()
