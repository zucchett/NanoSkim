#!/usr/bin/env python
import os, glob, sys
from commands import getoutput
import re
import datetime
import subprocess
import itertools
from utils import *

import optparse
usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-f', '--filter', action='store', type='string', dest='filter', default="")
(options, args) = parser.parse_args()

samples = open(FILELIST+".txt", "r").read().splitlines()
if len(options.filter) > 0: samples = [x for x in samples if options.filter in x]

if not os.path.exists(FILELIST): os.mkdir(FILELIST)

for s in samples:
    if len(s) == 0: continue
    if s.startswith('#'): continue
#    if not '/' in s: continue
#    dataset, campaign, format = s.split('/')[1:]
    
    # get filelist
    query = 'das_client --limit=0 --query="file dataset=%s"' % (s,)
    #print "Executing ", query
    output = getoutput(query)
    outputList = output.split(os.linesep)
    fileList = [x for x in outputList if x.endswith(".root")]
    
    fileName = getNameFromDAS(s)#FILELIST+"/"+dataset+"_"+campaign+".txt"
    with open(FILELIST + "/" + fileName + ".txt", "w") as f:
        for l in fileList:
            f.write("%s\n" % l)
    print " - Wrote", len(fileList), "files for", fileName
    
#    # get number of events
#    query = 'das_client --limit=0 --query="summary dataset=%s"' % (s,)
#    #print "Executing ", query
#    output = getoutput(query)
#    print output[0]["nevents"]
    
print "+ Done."

# voms-proxy-init --voms cms --valid 168:00
