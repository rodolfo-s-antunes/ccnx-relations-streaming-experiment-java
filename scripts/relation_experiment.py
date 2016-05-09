#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, time
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

class ExperimentRun:
	def __init__(self, cd):
		self.name = cd['name']
		self.ccnprefix = cd['ccnprefix']
		self.clients = cd['clients']
		self.vblksize = cd['vblksize']
		self.ablksize = cd['ablksize']
		self.buffersize = cd['buffersize']
		self.streamrate = cd['streamrate']
		self.streamsize = cd['streamsize']
		self.launchdelay = cd['launchdelay']
		self.vobj = cd['vobj']
		self.audiolist = cd['audiolist']
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
		objpos = 0
		nextlaunch = np.random.poisson(1)
		while clcount < self.clients:
			auxconf = '%s '%self.name
			auxconf += '%s/%s '%(self.ccnprefix,self.vobj)
			auxconf += '%d '%self.vblksize
			auxconf += '%d '%self.buffersize
			auxconf += '%d '%self.streamrate
			auxconf += '%s '%self.audiolist[objpos]
			auxconf += '%d '%self.ablksize
			auxconf += '%d '%self.buffersize
			auxconf += '%d '%self.streamrate
			auxconf += '%d'%nextlaunch
			result[CLIENTS[clpos]].append(auxconf)
			clcount += 1
			clpos = (clpos+1)%(len(CLIENTS))
			objpos = (objpos+1)%(len(self.audiolist))
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
		os.system('fab -H %s relation_run:%s,%d,%d'%(genHosts(),self.name,self.run,ltime))
		return
	def getResults(self):
		os.system('fab -H %s get_results:%s,%d'%(genHosts(),self.name,self.run))
		return

'''
def relation_files(name, aobjs, ccnprefix, vbsize, absize, blocks):
   with cd('rsantunes_temp'):
      alist = aobjs.split(':')
      vfname = '%s-video'%(name)
      vpname = '%s/%s'%(ccnprefix,vfname)
      run('dd if=/dev/urandom of=%s bs=%s count=%s'%(vfname, vbsize, blocks))
      run('ccnputfile %s %s'%(vpname, vfname))
      arqr = open('/tmp/temp-relations', 'w')
      for aobj in alist:
         fname = '%s-audio-%s'%(name,aobj)
         pname = '%s/%s'%(ccnprefix,fname)
         arqr.write('%s\t%s\n'%(aobj,pname))
         run('dd if=/dev/urandom of=%s bs=%s count=%s'%(fname, absize, blocks))
         run('ccnputfile %s %s'%(pname, fname))
      arqr.close()
      put('/tmp/temp-relations', 'temp-relations')
      run('ccnputmeta %s %s %s'%(vpname, 'relations', 'temp-relations'))      
'''

class ContentFiles:
	def __init__(self, cd):
		self.name = cd['name']
		self.run = cd['run']
		self.ccnprefix = cd['ccnprefix']
		self.vbsize = cd['vblksize']
		self.audiolist = cd['audiolist']
		self.absize = cd['ablksize']
		self.blocks = cd['streamsize']
		self.vobj = '%s-run%s-video'%(self.name,self.run)
		return
	def publishFiles(self):
		vpname = '%s/%s'%(self.ccnprefix,self.vobj)
		os.system('fab -H %s publish_file:%s,%s,%d,%d'%(PUBLISHER,self.vobj,vpname,self.vbsize,self.blocks))
		arqr = open('/tmp/temp-relations', 'w')
		count = 0
		while count < len(self.audiolist):
			fname = '%s-run%s-audio%s'%(self.name,self.run,count)
			pname = '%s/%s'%(self.ccnprefix,fname)
			arqr.write('%s\t%s\n'%(self.audiolist[count],pname))
			os.system('fab -H %s publish_file:%s,%s,%d,%d'%(PUBLISHER,fname,pname,self.absize,self.blocks))
			count += 1
		arqr.close()
		os.system('fab -H %s publish_meta:%s,%s,%s'%(PUBLISHER,'/tmp/temp-relations',vpname,'relations'))
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
				for kblk in self.vblksize:
					for audios in self.audiolists:
						for cachesizestep in self.ccndcachesize:
							for cachestallstep in self.ccndcachestall:
								self.setClock()
								self.setCCNDParms(cachesizestep, cachestallstep)
								cd = self.__genConfDict(cln, kblk, audios, runcount)
								cf = ContentFiles(cd)
								cf.resetRepo()
								cf.publishFiles()
								cd['vobj'] = cf.vobj
								er = ExperimentRun(cd)
								er.deployConfs()
								collector = self.__launchCollector(cd['name'], cd['run'])
								er.runExperiment()
								self.__termCollector(collector)
								er.getResults()
			runcount += 1
		return
	def __setParameters(self):
		# Um nome para o experimento
		self.name = 'final_relations'
		# Prefixo CCN para armazenar os arquivos
		self.ccnprefix = 'ccnx:/rnp.br'
		# Número de clientes a serem instanciados
		self.clients = [20, 40, 60, 80, 100, 120]
		# Tamanho do bloco de memória utilizado para o vídeo
		self.vblksize = {'480':172*1000}
		# Tamanho do bloco de memória utilizado para o áudio
		self.ablksize = {'480':16*1000}
		# Tamanho do buffer dos clientes em blocos de memória
		self.buffersize = 6
		# Taxa do stream em blocos de memória por segundo
		self.streamrate = 1
		# Tamanho de blocos do arquivo de stream
		self.streamsize = 60
		# Listas de áudios utilizadas para busca de relações
		self.audiolists = [[str(y) for y in range(x)] for x in [20]] #[8,16,24,32,40,48,56,64]]
		# Intervalo de tempo em segundos para início dos clientes
		self.launchdelay = 10
		# Início das rodadas
		self.runmin = 1
		# Fim das rodadas
		self.runmax = 4
		# Tamanho da cache do CCND
		self.ccndcachesize = 10000
		# Tempo para stall dos objetos (segundos)
		self.ccndcachestall = 60
		return
	def __genConfDict(self, clients, quality, audios, runnumber):
		res = dict()
		res['name'] = '%s-%s-cln%s-auq%s'%(self.name, quality, clients, len(audios))
		res['ccnprefix'] = self.ccnprefix
		res['clients'] = clients
		res['vblksize'] = self.vblksize[quality]
		res['ablksize'] = self.ablksize[quality]
		res['buffersize'] = self.buffersize
		res['streamrate'] = self.streamrate
		res['streamsize'] = self.streamsize
		res['audiolist'] = audios
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
