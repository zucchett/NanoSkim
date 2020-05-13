#!/usr/bin/env python

import os, sys
from global_paths import *
from ROOT import TH1, TH1F, TH1D, TFile, TTree, TChain
from utils import *

import optparse
usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-f', '--filter', action='store', type='string', dest='filter', default="")
(options, args) = parser.parse_args()

EV = {}

samples = open(FILELIST+".txt", "r").read().splitlines()
if len(options.filter) > 0: samples = [x for x in samples if options.filter in x]

if not os.path.exists(FILELIST): os.mkdir(FILELIST)

for s in samples:
    if len(s) == 0: continue
    if s.startswith('#'): continue
    sampleName = getNameFromDAS(s)

    if "Run201" in sampleName:
        EV[sampleName] = 1.
        continue

#        if not '/' in s: continue
#        dataset, campaign, format = s.split('/')[1:]
#        sample = s.replace('/', '_')
#        if sample.startswith('_'): sample = sample[1:]
    

#    # get number of events
#    query = 'das_client --limit=0 --query="summary dataset=%s"' % (s,)
#    #print "Executing ", query
#    output = getoutput(query)
#    print output[0]["nevents"]

#        chain = TChain("Runs")
#        with open(FILELIST + "/" + sampleName + ".txt", "r") as l:
#            fileList = l.read().splitlines()
#            for ff in fileList:
#                chain.Add(LOCALSITE + ff)
#            genH = TH1D("genH_%s" % sampleName, "", 1, 0, 0)
#            genH.Sumw2()
##            chain.Draw("genEventCount>>genH_%s" % sampleName, "", "goff")
#            chain.Draw("genEventSumw>>genH_%s" % sampleName, "", "goff")
#            genEv = genH.GetMean()*genH.GetEntries()
#            print "+ Sample", sampleName, "has", genEv, "events"
#            f.write("%s\t%d\n" % (sampleName, genEv, ))
#            l.close()
    
    genEv = 0.
    nfiles = 0
    with open(FILELIST + "/" + sampleName + ".txt", "r") as l:
        fileList = l.read().splitlines()
        chain = TChain("Runs")
        for ff in fileList:
            chain.Add(LOCALSITE + ff)
            filename = ff.split('/')[-1].replace(".root", "")
            genH = TH1D("genH_%s" % filename, "", 1, 0, 0)
            genH.Sumw2()
            chain.Draw("genEventSumw>>genH_%s" % filename, "", "goff")
            genEv += genH.GetMean()*genH.GetEntries()
            chain.Reset()
            nfiles += 1
            print ' + ', sampleName[:25], ' '*10, nfiles, ' '*10, '\r',
    EV[sampleName] = genEv
    print ''
    print "+ Sample", sampleName[:25], "has", genEv, "events"
#                tmpf = TFile("root://cms-xrd-global.cern.ch/" + ff, "READ")
#                hist = TH1F(ff, "", 1, 0, 0)
#                tree = tmpf.Get("Events")
#                tree.Project(ff, "LHEWeight_originalXWGTUP/abs(LHEWeight_originalXWGTUP)", "")
#                genEv = hist.GetMean()*hist.GetEntries()
#                tmpf.Close()
#                print ' + ', sampleName[:20], '\t', nfiles, '\r',
#                nfiles += 1
#                nEv += genEv

    # Write to file
#with open(MAINDIR + "/" + FILELIST + "/Events.txt", "w") as f:
#    for s, ev in EV.iteritems():
#        f.write("%s\t%d\n" % (s, ev, ))
#    l.close()

print EV

print "+ Done."

# voms-proxy-init --voms cms --valid 168:00



#runTree = treeFile.Get('Runs')

#        genH = TH1D("genH_%s" % sample, "", 1, 0, 0)
#        genH.Sumw2()

#        runTree.Draw("genEventCount>>genH_%s" % sample, "", "goff")
#        genEv = genH.GetMean()*genH.GetEntries()
#        
#        # Cross section
#        XS = getXsec(sample)
#        #SF = getSF(sample)
#        
#        Leq = LUMI*XS/genEv if genEv > 0 else 0.
