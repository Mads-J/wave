"""
Overview
--------

This module provides an interface to data stored in the XMDF output files
generated by CMS-Wave and CMS-Flow.  The XMDF data format is built upon HDF5 and
is readable using HDF tools.

**Development Status:**
  **Last Modified:** October 18, 2010 by Charlie Sharpsteen

"""


#------------------------------------------------------------------------------
#  Imports from Python 2.7 standard library
#------------------------------------------------------------------------------
from datetime import datetime
from os import path
import re

#------------------------------------------------------------------------------
#  Imports from third party libraries
#------------------------------------------------------------------------------
import h5py
import numpy

#------------------------------------------------------------------------------
#  Imports from other CMS submodules
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#  Data Retrieval
#------------------------------------------------------------------------------
def load_cms_data(cmcardsPath):
  cms_props = scan_cmcards(cmcardsPath)

  return cms_props


def scan_cmcards(cmcardsPath):
  sim_folder = path.dirname(path.abspath( cmcardsPath ))
  cmcardsFile = open(cmcardsPath, 'r')

  cmcards = cmcardsFile.read().splitlines()
  cmcardsFile.close()

  # Pull out the date components from cmcards.
  dateComponents = [ id_component( line ) for line in cmcards 
    if re.search('JDATE', line) and not line.startswith('!') ]

  # There should only be two components.
  if len(dateComponents) != 2:
    raise RuntimeError('''Did not find exactly 2 JDATE cards in the cmcards
    file.  This violates assumptions made by scan_cmcards()!  Cowardly refusing
    to continue execution.''')

  # Sneaky trick to merge the two dictionaries contained in the dateComponents list.
  dateComponents = dict( dateComponents[0], **dateComponents[1] )

  # Collapse to a string.
  datestamp = '{date} {hour}'.format(**dateComponents)

  # Transform to an actual datestamp.
  start_time = datetime.strptime( datestamp, '%y%j %H' )

  # Get CMS-Flow info:
  current_data = dataset_from_cmcards('GLOBAL_VELOCITY_OUTPUT', cmcards, 'currents')
  sse_data = dataset_from_cmcards('GLOBAL_WATER_LEVEL_OUTPUT', cmcards, 'sse')

  # Combine into one hash.
  h5data = current_data
  h5data.update( sse_data )

  # Figure out if CMS-Wave output is present by looking to see if the output
  # times was set to a non-zero list number.
  haveWaveOutput = [ re.split('\s+', line)[1] 
    for line in cmcards 
    if line.startswith('WAVES_OUT_TIMES_LIST') ].pop()

  # It is currently assumed that all output is contained in the same HDF5 file
  # as the currents.
  if not path.dirname(current_data['file']):
    h5file = path.join(sim_folder, current_data['file'])
  else:
    h5file = current_data['file']

  h5data['file'] = h5file

  return {'start_time': start_time, 'output': h5data}


#---------------------------------------------------------------------
#  Utility Functions
#---------------------------------------------------------------------
def id_component( dateComponent ):
  # Should be a tag and a value
  dateComponent = re.split('\W+', dateComponent)[0:2]

  if dateComponent[0].endswith('HOUR'):
    return {'hour': dateComponent[1]}
  else:
    return {'date': dateComponent[1]}

def dataset_from_cmcards( setID, cmcards, shortName ):
  # Find the h5 output info by looking for a card that starts with the string
  # contained in setID In case this line has been specified more than once, will
  # take the last occurance in the file by using pop().
  h5info = [ line for line in cmcards if line.startswith(setID) ].pop()

  # Split it into words and return the first three chunks, then clean any quotes
  # form those chunks.
  h5info = [ re.sub('\"|\'', '', string)
    for string in re.split('\s+', h5info)[0:3] ]

  return {'file': h5info[1], '{0}_path'.format(shortName): h5info[2]}

