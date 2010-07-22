#!/usr/bin/env python
"""
-------------------------------------------------------------------
This script retrieves buoy data from the NDBC.

Version:       0.1.0
Author:        Charlie Sharpsteen <source@sharpsteen.net>
Last Modified: July 20, 2010 by Charlie Sharpsteen
-------------------------------------------------------------------
"""

import sys
if sys.version_info < (2, 7):
  import warnings
  warnings.warn( '''This script was develped on python 2.7, 
                    there may be bugs with earlier versions!''' )

# Make sure the WaveConnect py/lib folder is on the search path so
# modules can be retrieved.
sys.path.insert( 1, '../lib' )


import datetime

import json
    

from wavecon import DBman
from wavecon import NDBC


"""
-------------------------------------------------------------------
   Utility Functions
-------------------------------------------------------------------
"""
def ISO_datestring( aString ):
  """Takes a string in 'unambiguous format' and returns a datetime object.

  Here, 'unambiguous format' is arbitrarily declared to be that used by R if
  no format specification is provided:

     %m/%d/%Y %H:%M:%S

  """

  return datetime.datetime.strptime( aString, '%m/%d/%Y %H:%M:%S' )


"""
-------------------------------------------------------------------
   Main Script and Supporting Functions
-------------------------------------------------------------------
"""
def processArgs():
  """Processes command-line arguments and returns a loaded ArgumentParser."""
  import argparse

  parser = argparse.ArgumentParser( description = 'BuoyBoy: A buoy data fetcher.' )

  # Flag arguments- these are optional and distinguished by -something
  parser.add_argument( '-v', action = 'store_true', dest = 'be_verbose',
                       help = 'Should BuoyBoy pretend he is called ChattyCathy?' )

  # Positional arguments- these are not identified by a flag.  Rather their meaning is
  # inferred from their position in the command line.
  parser.add_argument( 'buoyNum', metavar = 'Buoy#', type = int,
                       choices = [46022, 46212, 46244],
                       help = 'The number of the NDBC buoy for which you wish to fetch data.' )

  parser.add_argument( 'startTime', metavar = 'StartTime', type = ISO_datestring,
                        help = '''The starting time for data you wish to download. Must be in the 
                        following format "month/day/year hour:minute:second"''' )
  parser.add_argument( 'stopTime', metavar = 'StopTime', type = ISO_datestring,
                        help = '''The end of the time range for which data is to be downloaded. 
                        Uses the same format as described above.''' ) 

  args = parser.parse_args()
  return args


def loadDBConfig():
  """Looks for a file called dbconfig.json that stores database logon info."""
  
  try:
    configFile = open( 'dbconfig.json', 'r' )
  except:
    print """\nOh noes!  Could not find database accees credentials!  I was looking\
for the file:\n\n\tdbconfig.json\n\nUnfortunately, this file is currently\
required and required to be in the working directory. \n"""
    sys.exit()

  DBconfig = json.load( configFile )
  return DBconfig


if __name__ == '__main__':
  """
  This is the actual script part.  Building a script file this way allows it to be used
  as both a command line tool and a python library.  Then other Python scripts can import
  functions from this one without running the script.
  """
  
  args = processArgs()
  DBconfig = loadDBConfig()

  print "\n\nHello, world!\n"

  tblWind = DBman.getDBTable( DBconfig, 'tblwind' )
  print tblWind.columns

  #windData = fetchFromNDBC( args.buoyNum, args.startTime, args.stopTime, 'wind' )

  #checkForDate = lambda obj: obj.isoformat() if isinstance( obj, datetime.datetime ) else None
  #print json.dumps( windData, indent = 4, default = checkForDate )

  #print "\n\n Stats: %i objects for %i days worth of data.\n" % ( len(windData), (args.stopTime - args.startTime).days )