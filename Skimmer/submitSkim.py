#!/bin/env python

import os, sys
from global_paths import *
from utils import *

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)

parser.add_option("-f", "--filter", action="store", type="string", dest="filter", default="", help="Specify a string to filter the datasets")
parser.add_option("-y", "--year", action="store", type="string", dest="year", default="", help="Filter datasets according to the year")
parser.add_option("-l", "--local", action="store_true", dest="local", default=False, help="Submit as local jobs")
parser.add_option("-n", "--nFilesPerJob", action="store", type=int, dest="nfiles", default=5, help="Set number of files per job")
parser.add_option("-q", '--queue', action='store', type="string", dest="queue", default="local-cms-short", help="Specify submission queue")
parser.add_option("-t", "--test", action="store_true", dest="test", default=False, help="Test run, executes the script but does not submit jobs")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Increase verbosity")
(options, args) = parser.parse_args()


# Make the proxy visible on LSF nodes
os.system("cp " + TEMPPROXY + " " + USERPROXY) # Copy certificate to lustre
os.environ['X509_USER_PROXY'] = USERPROXY # Set environment variable

def runSampleLSF(s):
    outputDir = OUTDIR + "/" + s + "/"
    command = "echo \"python " + MAINDIR + "/skim.py -l " + MAINDIR + "/" + FILELIST + "/" + s + ".txt -o " + outputDir + "\" | bsub -J " + s + " -oo " + LOGDIR + "/outfile_%J.txt -eo " + LOGDIR + "/errorfile_%J.txt -cwd " + LSFDIR + " -q " + options.queue + ""
    if not options.test: os.system(command)
    else: print "\n", command


def runFileLSF(s):
    outputDir = OUTDIR + "/" + s + "/"
    #if not options.test: os.system("rm -rf " + outputDir)
    with open(FILELIST + "/" + s + ".txt", "r") as f:
        i = 0
        flist = ""
        lines = f.read().splitlines()
        i, last = 0, len(lines)
        for f in lines:
            if len(f) == 0: continue
            flist += f + ','
            if (i > 0 and i % options.nfiles == 0) or i == last-1:
                command = "echo \"python " + MAINDIR + "/skim.py -i " + flist + " -o " + outputDir + "\" | bsub -J " + s + " -oo " + LOGDIR + "/outfile_%J.txt -eo " + LOGDIR + "/errorfile_%J.txt -cwd " + LSFDIR + " -q " + options.queue + ""
                if options.local: command = "python skim.py -i " + flist + " -o " + outputDir + " &> " + LOGDIR + "/localfile_" + s + ".txt &"
                if not options.test: os.system(command)
                elif options.verbose: print "\n", command, "\n"
                flist = ""
            i += 1


for s in SAMPLES:
    if len(s) <= 0 or s.startswith('#'): continue
    if len(options.filter) > 0 and not options.filter in s: continue
    print s
    if "2016" in options.year and not "Run2016" in s and not "Summer16" in s: continue
    if "2017" in options.year and not "Run2017" in s and not "Fall17" in s: continue
    if "2018" in options.year and not "Run2018" in s and not "Autumn18" in s: continue
    if not s in EV_v7 or not s in XS:
        print "- ERROR: sample", s, "has no events or cross section information, skipping..."
        continue
    print "+ Submitting", s
    runFileLSF(s)


if not options.test: print "+ Done."
else: print "+ Test ended, no job submitted."


# voms-proxy-init --rfc --voms cms --valid 168:00
