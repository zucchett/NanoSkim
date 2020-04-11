#!/bin/env python

import os, sys
from global_paths import *

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)

parser.add_option("-q", '--queue', action='store', type="string", dest="queue", default="local-cms-short")
parser.add_option("-r", "--resubmit", action="store_true", dest="resubmit", default=False)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
(options, args) = parser.parse_args()

queue = options.queue
resubmit = options.resubmit

ndone, nfail, nempty, nresub = 0, 0, 0, 0

for f in os.listdir(LOGDIR):
    if not f.startswith("outfile"): continue
    if not os.path.getsize(LOGDIR + '/' + f) > 0:
        nempty += 1
        continue
    
    number = f.split('_')[1].replace('.txt', '')
    
    isDone = False
    subject = ""
    node = ""
    command = ""
    with open(LOGDIR + '/' + f, "r") as r:
        for l in r.read().splitlines():
            if "+ Done." in l: isDone = True
            if l.endswith("Exited"): subject = l
            if l.startswith("Sender:"): node = l.replace("Sender: LSF System ", "")
            if l.startswith("python "): command = l
        if isDone:
            ndone += 1
            print "Success job", f, "Node:", node
        else:
            nfail += 1
            print "Failed  job", f, "Node:", node, "Exit code:", subject
            if resubmit:
                targetdir = command.split('-o ')[1]
                jobname = targetdir.split('/')[-2]
                if len(jobname) == 0: jobname = "resub"
                recommand = "echo \"" + command + "\" | bsub -J " + jobname + " -oo " + LOGDIR + "/outfile_%J.txt -eo " + LOGDIR + "/errorfile_%J.txt -cwd " + LSFDIR + " -q " + queue + ""
                os.system("rm " + LOGDIR + "/*" + number + "*")
                os.system("rm -rf " + LSFDIR + "/*" + number + "*")
                #os.system("rm -rf " + targetdir)
                os.system(recommand)
                nresub += 1

    r.close()
        

print "Number of successful / failed / empty jobs:", ndone, '/', nfail, '/', nempty, '(', float(ndone)/(ndone + nfail + nempty)*100., '%)'
if resubmit: print "Resubmitted", nresub, "jobs"

# voms-proxy-init --rfc --voms cms --valid 168:00
