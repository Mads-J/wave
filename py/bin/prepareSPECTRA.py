#!/usr/bin/env python

################################
# FILENAMES
################################
cmsdir = '/Users/naftali/Desktop/CMS/bin'
simfile = 'WAVE.sim'
depfile = 'WAVE.dep'
cardfile = 'FLOW.cmcards'
steeringinterval = 3 #hours

################################
# IMPORT MODULES
################################
import sys #argument parsing
import datetime #posix support
import glob #file wildcard support
import re #regex support
from numpy import * #math support
from geoalchemy import *
from geoalchemy.postgis import pg_functions
from geoalchemy.functions import functions
from os import path,system,remove
strptime = datetime.datetime.strptime

################################
# IMPORT DATABASE FUNCTIONS
################################
DBman_path = path.abspath('.')+'/../lib/'
sys.path.insert( 0, DBman_path )
from wavecon import DBman
from wavecon.config import DBconfig

################################
# DETERMINE SPATIAL DOMAIN
################################
#get origin
simfile = glob.glob(cmsdir + '/' + simfile)[0]
lines = open(simfile).read()
pat = re.compile("(-*\d+\.*\d*)")
match = pat.findall(lines)
lon_ll = float(match[0])
lat_ll = float(match[1])
#get grid size
depfile = glob.glob(cmsdir + '/' + depfile)[0]
lines = open(depfile).read()
pat = re.compile(".*?(\d+\.*\d*)")
match = pat.findall(lines)
nx = int(match[0])
ny = int(match[1])
delta_x = float(match[2])
delta_y = float(match[3])
#calculate ur corner
lon_ur = lon_ll + (nx-1)*delta_x 
lat_ur = lat_ll + (ny-1)*delta_y 
#create box2d object
point_ll = 'ST_SETSRID(ST_POINT('+str(lon_ll)+','+str(lat_ll)+'),32610)'
point_ur = 'ST_SETSRID(ST_POINT('+str(lon_ur)+','+str(lat_ur)+'),32610)'
box = 'ST_SETSRID(ST_MAKEBOX2D('+point_ll+','+point_ur+'),32610)'

################################
# DETERMINE TEMPORAL DOMAIN
################################
cardfile = glob.glob(cmsdir + '/' + cardfile)[0]
lines = open(cardfile).read()
pat1 = re.compile("STARTING_JDATE.*?(\d{8})")
pat2 = re.compile("STARTING_JDATE_HOUR.*?(\d+)")
pat3 = re.compile("DURATION_RUN.*?(\d+)")
startdy = pat1.findall(lines)[0]
starthr = pat2.findall(lines)[0]
durationrun = pat3.findall(lines)[0]
durationrun = float(durationrun)
durationrun = datetime.timedelta(durationrun/24.0)
steeringinterval = datetime.timedelta(steeringinterval/24.0)
starttime = startdy + starthr
starttime = strptime( starttime, '%Y%m%d%H' )
stoptime = starttime + durationrun
steeringtimes = []
steeringtimes2 = []
mytime = starttime
while( mytime <= stoptime):
  steeringtimes.append(mytime)
  mytime = mytime+steeringinterval
starttime = starttime.strftime('%Y%m%d %H:00' )
stoptime = stoptime.strftime('%Y%m%d %H:00' )
starttime = '(TIMESTAMP \''+starttime+'\')'
stoptime = '(TIMESTAMP \''+stoptime+'\')'

################################
# RETREIVE DATA FROM TBLWAVE
################################
spec,specid,wavtime,wavloc,wavx,wavy = [[],[],[],[],[],[]]
session = DBman.startSession( DBconfig )
q1 = ' select wavid from tblwave where ST_WITHIN('
q2 = ' ST_TRANSFORM(wavlocation,32610),' + box + ') '
q3 = ' and wavdatetime>='+starttime
q4 = ' and wavdatetime<='+stoptime
q5 = q1+q2+q3+q4
q6 = ' select wavspectra,wavspectraid,'
q7 = ' wavdatetime,wavlocation,'
q8 = ' ST_X(ST_TRANSFORM(wavlocation,32610)),'
q9 = ' ST_Y(ST_TRANSFORM(wavlocation,32610)) ' 
q10 = 'from tblwave where wavid in ('+q5+')'
q11 = q6+q7+q8+q9+q10
result = session.execute(q11).fetchall()
for k in range(len(result)):
  spec.append(result[k][0]) 
  specid.append(result[k][1]) 
  wavtime.append(result[k][2])
  wavloc.append(result[k][3])
  wavx.append(result[k][4])
  wavy.append(result[k][5])
spec=array(spec)
specid=array(specid)
wavtime=array(wavtime)                            
wavloc=array(wavloc)
wavx=array(wavx)
wavy=array(wavy) 

################################
# RETREIVE FREQ/DIR BINS
################################
freq,dir = [[],[]]
for myspectraid in specid:
  q1 = "select spectrafreq,spectradir from "
  q2 = "tblspectra where spectraid='"+myspectraid+"'"
  q3 = q1+q2
  result = session.execute(q3).fetchall()
  freq.append(result[0][0])
  dir.append(result[0][1])
freq=array(freq)
dir=array(dir)
 
################################
# INTERPOLATE SPECTRA TO NEW
# DIRECTION BINS, CMS EXPECTS 
# HALF PLANE DIVIDED INTO 'N' BINS,
# FIRST BIN = TRAVELING SOUTH,
# MIDDLE BIN = TRAVELING EAST, 
# LAST BIN = TRAVELING NORTH 
################################
for k in range(len(spec)):
  filter = dir[k]>90
  dir[k][filter] = dir[k][filter]-360
  sortorder = argsort(dir[k])
  sorted_dirs = dir[k][sortorder]
  mydirs = linspace(-90,90,len(dir[k]))
  for f in range(len(spec[k])):
    sorted_spec = spec[k][f][sortorder]
    spec[k][f] = interp(mydirs,sorted_dirs,sorted_spec)

################################
# FOR EACH SPECTRA, FIND PEAK FREQUENCY
################################
peakfreqindex = spec.max(1).argmax(1)
peakfreq = []
for index in peakfreqindex:
  peakfreq.append(freq[k][index])

################################
# ARRANGE SPEC BY LOCATION, THEN TIME
################################
locset = [x for x in set(wavloc)]
sortorder = argsort(locset)
locset = array(locset)[sortorder]                 
#WRITE METAFILE HEADER
metafn = 'nest.meta'
metafile = open(metafn,'w')
metafile.write('nest.dat\n')
metafile.write(str(len(locset))+'\n0\n')
counter=0
for myloc in locset:
  #CHECK THAT ALL FREQUENCY BINS MATCH
  filter = (wavloc==myloc)
  myfreq = freq[filter].tolist()
  nf = len(myfreq[0])
  nd = len(mydirs)
  myfreqstr = [' '.join([str(i) for i in f]) for f in myfreq]
  if (len(set(myfreqstr))>1):
    quit('error: frequency bin mismatch!')
  fn = 'WAVE.'+str(counter)+'.eng'
  counter=counter+1
  #ADD META DATA TO METAFILE
  myx = set(wavx[filter])
  myy = set(wavy[filter])
  if (len(myx)>1 or len(myy)>1):
    quit('error: coordinate mismatch!') 
  myx = wavx[filter][0]
  myy = wavy[filter][0]
  metafile.write(fn+'\n')
  metafile.write(str(myx)+' '+str(myy)+'\n')
  #WRITE SPEC FILE HEADER
  file=open(fn,'w')
  file.write( str(nf) + ' ' + str(nd) + '\n' )
  file.write( myfreqstr[0] + '\n')
  #WRITE CONSECUTIVE TIMESTEPS TO FILE 
  for mytime in steeringtimes:
    filter = logical_and( wavloc==myloc, wavtime==mytime)
    if (all(filter==False)):
      #CANT HANDLE MISSING DATA
      quit('\n\nno data exists for time: '+str(mytime)+
          '\n\nsuggested steering interval: '+str(wavtime[1]-wavtime[0]))
    else:
      #WRITE SINGLE TIMESTEP DATA TO SPEC FILE
      filter = filter.tolist().index(True) 
      line = ' '.join([
        mytime.strftime('%Y%m%d%H'),'0','0',
        str(peakfreq[filter]),'0'])
      file.write(line+'\n')
      for f in range(len(freq[filter])):
        line = ' '.join([str(d) for d in spec[filter][f]])
        file.write('\t'+line+'\n')
  file.close()
metafile.close()

################################
# MERGE ENG FILES
################################
command = './mergeENG.exe < '+metafn
print command
system(command)
system('rm *.eng; touch WAVE.eng') 
