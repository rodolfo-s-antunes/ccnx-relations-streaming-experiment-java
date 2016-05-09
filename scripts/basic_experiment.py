#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, time
import random, bisect, math 
import subprocess as sp
import numpy as np

# Esta lista contém o nome dos clientes na ordem em que eles serão
# preenchidos. Esta ordem segue a ideia de distribuir os clientes
# em largura dentro da árvore de transmissão centrada em MG.
STATES = ['ce', 'df', 'sp', 'ba', 'ma', 'rn', 'go', 'rj', 'am', 'pr', 'rr', 'sc', 'es', 'se', 'pa', 'pb', 'mt', 'to', 'ms', 'rs', 'al', 'ap', 'pi', 'ro', 'pe', 'ac']
#STATES = ['rs']
CLIENTS = ['ccn_'+x for x in STATES]
PUBLISHER = 'ccn_mg'

def genHosts():
	result = ""
	for cl in CLIENTS:
		result += "%s,"%cl
	return result[:-1]

class ZipfGenerator: 
   def __init__(self, n, alpha): 
      # Calculate Zeta values from 1 to n: 
      tmp = [1. / (math.pow(float(i), alpha)) for i in range(1, n+1)] 
      zeta = reduce(lambda sums, x: sums + [sums[-1] + x], tmp, [0]) 
      # Store the translation map: 
      self.distMap = [x / zeta[-1] for x in zeta] 
   def next(self): 
      # Take a uniform 0-1 pseudo-random value: 
      u = random.random()
      # Translate the Zipf variable: 
      return bisect.bisect(self.distMap, u)-1

class ExperimentRun:
	def __init__(self, cd):
		self.name = cd['name']
		self.ccnprefix = cd['ccnprefix']
		self.clients = cd['clients']
		self.blksize = cd['blksize']
		self.buffersize = cd['buffersize']
		self.streamrate = cd['streamrate']
		self.streamsize = cd['streamsize']
		self.launchdelay = cd['launchdelay']
		self.objlist = cd['objlist']
		self.run = cd['run']
		return
	def __initClientDict(self):
		result = dict()
		for cl in CLIENTS:
			result[cl] = list()
		return result
	def __generateConfs(self):
		result = self.__initClientDict()
		clcount = 0
		clpos = 0
		#objpos = 0
		objdist = ZipfGenerator(len(self.objlist),2)
		nextlaunch = np.random.poisson(1)
		while clcount < self.clients:
			auxconf = '%s '%self.name
			#auxconf += '%s/%s '%(self.ccnprefix,self.objlist[objpos])
			auxconf += '%s/%s '%(self.ccnprefix,self.objlist[objdist.next()])
			auxconf += '%d '%self.blksize
			auxconf += '%d '%self.buffersize
			auxconf += '%d '%self.streamrate
			auxconf += '%d'%nextlaunch
			result[CLIENTS[clpos]].append(auxconf)
			clcount += 1
			clpos = (clpos+1)%(len(CLIENTS))
			#objpos = (objpos+1)%(len(self.objlist))
			nextlaunch += np.random.poisson(1)
		return result
	def deployConfs(self):
		clients = self.__generateConfs()
		for clk in clients:
			carq = open('/tmp/experiment.conf', 'w')
			for linha in clients[clk]:
				carq.write('%s\n'%linha)
			carq.close()
			os.system('fab -H %s copy_configuration:/tmp/experiment.conf'%clk)
		return
	def runExperiment(self):
		ltime = int(time.time())+self.launchdelay
		os.system('fab -H %s basic_run:%s,%d,%d'%(genHosts(),self.name,self.run,ltime))
		return
	def getResults(self):
		os.system('fab -H %s get_results:%s,%d'%(genHosts(),self.name,self.run))
		return

class ContentFiles:
	def __init__(self, cd):
		self.name = cd['name']
		self.run = cd['run']
		self.ccnprefix = cd['ccnprefix']
		self.filequant = cd['filequant']
		self.bsize = cd['blksize']
		self.blocks = cd['streamsize']
		self.filelist = self.__getFileList()
		return
	def __getFileList(self):
		result = list()
		count = 1
		while count <= self.filequant:
			result.append('%s-run%s-file%s'%(self.name,self.run,count))
			count += 1
		return result
	def publishFiles(self):
		for fname in self.filelist:
			pname = '%s/%s'%(self.ccnprefix,fname)
			os.system('fab -H %s publish_file:%s,%s,%d,%d'%(PUBLISHER,fname,pname,self.bsize,self.blocks))
		return
	def resetRepo(self):
		os.system('fab -H %s reset_repo'%PUBLISHER)
		return
		
class Main:
	def __init__(self):
		self.__setParameters()
		runcount = self.runmin
		while runcount <= self.runmax:
			for cln in self.clients:
				for kblk in self.blksize:
					for flq in self.filequant:
						for cachesizestep in self.ccndcachesize:
							for cachestallstep in self.ccndcachestall:
								self.setClock()
								self.setCCNDParms(cachesizestep, cachestallstep)
								cd = self.__genConfDict(cln, kblk, self.blksize[kblk], flq, runcount, cachesizestep, cachestallstep)
								cf = ContentFiles(cd)
								cf.resetRepo()
								cf.publishFiles()
								cd['objlist'] = cf.filelist
								er = ExperimentRun(cd)
								er.deployConfs()
								collector = self.__launchCollector(cd['name'], cd['run'])
								er.runExperiment()
								self.__termCollector(collector)
								er.getResults()
			runcount += 1
		self.objlist = cd['objlist']
		return
	def __setParameters(self):
		# Um nome para o experimento
		self.name = '8obj'
		# Prefixo CCN para armazenar os arquivos
		self.ccnprefix = 'ccnx:/rnp.br'
		# Número de clientes a serem instanciados
		self.clients = [130]
		# Tamanho do bloco de memória utilizado pelos clientes
		self.blksize = {'480':188*1000}
		# Tamanho do buffer dos clientes em blocos de memória
		self.buffersize = 12
		# Taxa do stream em blocos de memória por segundo
		self.streamrate = 1
		# Tamanho de blocos do arquivo de stream
		self.streamsize = 60
		# Número de arquivos a serem utilizados no experimento
		self.filequant = [8] # [8,16,24,32,40,48,56,64]
		# Intervalo de tempo em segundos para início dos clientes
		self.launchdelay = 10
		# Início das rodadas
		self.runmin = 1
		# Fim das rodadas
		self.runmax = 2
		# Tamanho da cache do CCND
		self.ccndcachesize = [int((188/4)*60*8*x) for x in [0.02, 0.04, 0.06, 0.08, 0.10]]
		# Tempo para stall dos objetos (segundos)
		self.ccndcachestall = [60] # [10, 20, 40, 60]
		return
	def __genConfDict(self, clients, quality, blksize, filequant, runnumber, cachesize, cachetime):
		res = dict()
		res['name'] = '%s-%s-cln%s-flq%s-cs%s-ct%s'%(self.name, quality, clients, filequant, cachesize, cachetime)
		res['ccnprefix'] = self.ccnprefix
		res['clients'] = clients
		res['blksize'] = blksize
		res['buffersize'] = self.buffersize
		res['streamrate'] = self.streamrate
		res['streamsize'] = self.streamsize
		res['filequant'] = filequant
		res['launchdelay'] = self.launchdelay
		res['run'] = runnumber
		return res
	def setCCNDParms(self, cachesize, staletime):
		tempconf = open('/tmp/ccndrc', 'w')
		tempconf.write('CCND_CAP=%d\n'%cachesize)
		tempconf.write('CCND_DEFAULT_TIME_TO_STALE=%d\n'%staletime)
		tempconf.write('CCND_MAX_TIME_TO_STALE=%d\n'%staletime)
		tempconf.close()
		os.system('fab -H %s insert_ccndrc'%(genHosts()))
		os.system('fab -H %s insert_ccndrc'%(PUBLISHER))
		os.system('python asgardscripts/ccnd.py start')
		return
	def setClock(self):
		os.system('fab -H %s update_clock'%(genHosts()))
		os.system('fab -H %s update_clock'%(PUBLISHER))
		return
	def __launchCollector(self, name, run):
		args = 'python getRouterData.py %s %d 1'%(name,run)
		self.collog = open('collector.log', 'a')
		collector = sp.Popen(args, shell=True, stdout=self.collog)
		return collector
	def __termCollector(self, collector):
		collector.terminate()
		self.collog.close()
		return

if __name__ == '__main__': Main()
