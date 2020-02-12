#!/bin/env python

import os, sys

ndone, nfail, nempty = 0, 0, 0

for f in os.listdir('LSF/'):
    if not f.startswith("outfile"): continue
    if not os.path.getsize('LSF/' + f) > 0:
        nempty += 1
        continue
    isDone = False
    subject = ""
    with open('LSF/' + f, "r") as r:
        for l in r.read().splitlines():
            if "+ Done." in l: isDone = True
            if l.endswith("Exited"): subject = l
        if isDone: ndone += 1
        else:
            nfail += 1
            print "Failed job", f, ":", subject
    r.close()
#        

print "Number of successful / failed / empty jobs:", ndone, '/', nfail, '/', nempty, '(', float(ndone)/(ndone + nfail + nempty)*100., '%)'
