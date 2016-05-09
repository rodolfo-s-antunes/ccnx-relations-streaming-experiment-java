#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from datetime import datetime
from fabric.api import local, sudo, get, put, run, env, settings, parallel, hosts
from fabric.context_managers import cd

def gen_host_list():
  #suffixes = ['27.2', '26.2', '25.2', '16.2', '23.2', '22.2', '21.2', '20.2', '29.2', '17.2', '19.2', '18.2', '15.2', '15.1', '13.1', '11.2', '14.2', '1.2', '2.2', '3.2', '3.1', '10.2', '9.1', '4.2', '6.2', '7.2']
  #suffixes.append('16.1')
  #suffixes = ["17.2"]
  #return ['192.168.'+x for x in suffixes]
  states = ['ac', 'ro', 'mt', 'ms', 'go', 'to', 'pr', 'sc', 'rs', 'am', 'df', 'sp', 'rj', 'rr', 'ap', 'pa', 'ma', 'ce', 'rn', 'pb', 'pe', 'al', 'pi', 'ba', 'es', 'se']
  states += ['mg']
  return ['ccn_'+x for x in states]

#env.roledefs.update({'all':gen_host_list()+['ccn_mg']})
#env.roledefs.update({'clients':gen_host_list()})
#env.roledefs.update({'publisher':['ccn_mg']})
#env.hosts = gen_host_list()
env.user = 'gticn'
env.password = 'gticn'

def prepare_workspace():
   run('rm -rf workspace')
   run('mkdir workspace')
   run('mkdir workspace/prodcon')
   run('mkdir workspace/prodcon/lib')
   run('mkdir workspace/prodcon/bin')
   run('mkdir workspace/prodcon/src')
   run('mkdir workspace/prodcon/src/prodcon')
   run('mkdir workspace/prodcon/scripts')

def copy_libs():
   put('/home/gticn/workspace/prodcon/lib/*.jar', '/home/gticn/workspace/prodcon/lib/', mirror_local_mode=True)

def copy_scripts():
   put('/home/gticn/workspace/prodcon/scripts/*.py', '/home/gticn/workspace/prodcon/scripts/', mirror_local_mode=True)
   put('/home/gticn/workspace/prodcon/scripts/*.sh', '/home/gticn/workspace/prodcon/scripts/', mirror_local_mode=True)

def copy_experiment():
   put('/home/gticn/workspace/prodcon/src/prodcon/*.java', '/home/gticn/workspace/prodcon/src/prodcon/', mirror_local_mode=True)

def compile_experiment():
   run('javac -cp workspace/prodcon/lib/bcprov-jdk15-143.jar:workspace/prodcon/lib/ccn.jar -d workspace/prodcon/bin workspace/prodcon/src/prodcon/*.java')

#@roles('all')
def prepare_experiment():
   prepare_workspace()
   copy_libs()
   copy_scripts()
   copy_experiment()
   compile_experiment()

# argumentos do experimento em ordem:
# <BaseName>: utilizado para nomeação de arquivos de saída
# <Clients>: número de clientes instanciados
# <BlockSize>: tamanho do bloco em bytes
# <BufferSize>: tamanho do buffer em blocos
# <StreamRate>: taxa do stream em blocos por segundo
# <LaunchTime>: momento em que os clientes serão iniciados em unix standard time
# <FileList>: lista separada por vírgula dos arquivos que serão solicitados pelos clientes
# <RunNumber>: número da execução para nomeação de arquivos
#@roles('clients')
@parallel
def basic_experiment(basename, clients, blocksize, buffersize, streamrate, launchtime, filelist, runnumber):
   parms = '%s %s %s %s %s %s %s %s'%(basename, clients, blocksize, buffersize, streamrate, launchtime, filelist, runnumber)
   run('python workspace/prodcon/scripts/basic-experiment.py %s'%parms)

@parallel
def basic_run(basename, runnumber, launchtime):
   parms = '%s %s %s'%(basename, runnumber, launchtime)
   run('python workspace/prodcon/scripts/basic_run.py %s'%parms)

# argumentos em ordem:
# <BaseName>: utilizado para nomeação de arquivos de saída
# <Clients>: número de clientes instanciados
# <VideoBlockSize>: tamanho do bloco de video em bytes
# <AudioBlockSize>: tamanho do bloco de audio em bytes
# <BufferSize>: tamanho do buffer em blocos
# <StreamRate>: taxa do stream em blocos por segundo
# <LaunchTime>: momento em que os clientes serão iniciados em unix standard time
# <VideoObj>: caminho para o objeto de vídeo
# <AudioList>: lista separada por vírgula dos streams de audio que serão solicitados
# <RunNumber>: número da execução para nomeação de arquivos
#@roles('clients')
@parallel
def relation_experiment(basename, clients, vbs, abs, buffersize, streamrate, launchtime, vobj, alist, runnumber):
   parms = '%s %s %s %s %s %s %s %s %s %s'%(basename, clients, vbs, abs, buffersize, streamrate, launchtime, vobj, alist, runnumber)
   run('python workspace/prodcon/scripts/relation-experiment.py %s'%parms)

@parallel
def relation_run(basename, runnumber, launchtime):
   parms = '%s %s %s'%(basename, runnumber, launchtime)
   run('python workspace/prodcon/scripts/relation_run.py %s'%parms)

#@roles('publisher')
def reset_repo():
   with cd('rsantunes_temp'):
      with settings(warn_only=True):
         run('rm -f *')
   with cd('rsantunes_repo'):
      with settings(warn_only=True):
         pid = run('pidof ccnr')
         if not pid == '':
            run('kill %s'%pid)
         run('rm -r *')
      local('ssh ccn_mg sh workspace/prodcon/scripts/start_repo.sh')

#@roles('publisher')
def basic_files(name, ccnprefix, bs, blocks, quant):
   with cd('rsantunes_temp'):
      count = 1
      while (count <= int(quant)):
         fname = '%s-%s'%(name,count)
         pname = '%s/%s'%(ccnprefix,fname)
         run('dd if=/dev/urandom of=%s bs=%s count=%s'%(fname, bs, blocks))
         run('ccnputfile %s %s'%(pname, fname))
         count += 1

#@roles('publisher')
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

#@roles('publisher')
def publish_meta(fname, obj, metaname):
   with cd('rsantunes_temp'):
      auxname = fname.split('/')[-1]
      put(fname, auxname)
      run('ccnputmeta %s %s %s'%(obj, metaname, auxname))

#@roles('publisher')
def publish_file(fname, pname, bsize, blocks):
   with cd('rsantunes_temp'):
      run('dd if=/dev/urandom of=%s bs=%s count=%s'%(fname, bsize, blocks))
      run('ccnputfile %s %s'%(pname, fname))

def insert_ccndrc():
  put('/tmp/ccndrc', '.ccnx/ccndrc')

def get_results(name, runnumber):
   get('err-%s-%s.txt'%(name, runnumber), 'results/%s/%s'%(name,runnumber)+'/%(host)s/%(basename)s')
   get('out-%s-%s.txt'%(name, runnumber), 'results/%s/%s'%(name,runnumber)+'/%(host)s/%(basename)s')

def copy_configuration(filename='/tmp/experiment.conf'):
   put(filename)

def temp():
  run('rm .ssh/known_hosts')

def network_control(parm='start'):
  sudo('bash network.sh ' + parm)

def ccnd_status():
  run('ccndstatus')

def update_clock():
   now = datetime.now().strftime('%m%d%H%M%Y.%S')
   sudo('date %s'%now)

def ps(process='ccnr'):
  run('ps -ef | grep "%s"'%process)
