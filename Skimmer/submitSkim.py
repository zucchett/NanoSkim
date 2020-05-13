#!/bin/env python

import os, sys
from global_paths import *
from utils import *

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)

parser.add_option("-f", "--filter", action="store", type="string", dest="filter", default="")
parser.add_option("-n", "--nFilesPerJob", action="store", type=int, dest="nfiles", default=5)
parser.add_option("-y", "--year", action="store", type="string", dest="year", default="")
parser.add_option("-q", '--queue', action='store', type="string", dest="queue", default="local-cms-short")
parser.add_option("-t", "--test", action="store_true", dest="test", default=False)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
(options, args) = parser.parse_args()

skip = options.filter
year = options.year
nfiles = options.nfiles
queue = options.queue
test = options.test

# Make the proxy visible on LSF nodes
os.environ['X509_USER_PROXY'] = USERPROXY

def runSampleLSF(s):
    outputDir = OUTDIR + "/" + s + "/"
    command = "echo \"python " + MAINDIR + "/skim.py -l " + MAINDIR + "/" + FILELIST + "/" + s + ".txt -o " + outputDir + "\" | bsub -J " + s + " -oo " + LOGDIR + "/outfile_%J.txt -eo " + LOGDIR + "/errorfile_%J.txt -cwd " + LSFDIR + " -q " + queue + ""
    if not test: os.system(command)
    else: print "\n", command


def runFileLSF(s):
    outputDir = OUTDIR + "/" + s + "/"
    #if not test: os.system("rm -rf " + outputDir)
    with open(FILELIST + "/" + s + ".txt", "r") as f:
        i = 0
        flist = ""
        lines = f.read().splitlines()
        i, last = 0, len(lines)
        for f in lines:
            if len(f) == 0: continue
            flist += f + ','
            if i % nfiles == 0 or i == last-1:
                command = "echo \"python " + MAINDIR + "/skim.py -i " + flist + " -o " + outputDir + "\" | bsub -J " + s + " -oo " + LOGDIR + "/outfile_%J.txt -eo " + LOGDIR + "/errorfile_%J.txt -cwd " + LSFDIR + " -q " + queue + ""
                if not test: os.system(command)
                else: print "\n", command
                flist = ""
            i += 1


for s in SAMPLES:
    if len(s) <= 0 or s.startswith('#'): continue
    if len(skip) > 0 and not skip in s: continue
    if "2016" in year and not "Run2016" in s and not "Summer16" in s: continue
    if "2017" in year and not "Run2017" in s and not "Fall17" in s: continue
    if "2018" in year and not "Run2018" in s and not "Autumn18" in s: continue
    if not s in EV or not s in XS:
        print "- ERROR: sample", s, "has no events or cross section information, skipping..."
        continue
    if test: print "+ Submitting", s
    runFileLSF(s)


print "+ Done."



# voms-proxy-init --rfc --voms cms --valid 168:00
