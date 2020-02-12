#! /usr/bin/env python

import os, multiprocessing, math
from array import array
from ROOT import TFile, TH1, TF1, TLorentzVector, TObject

from utils import EV, XS, getNameFromFile

import optparse
usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--input', action='store', type='string', dest='origin', default='/lustre/cmswork/zucchett/Ntuple/v0/')
parser.add_option('-o', '--output', action='store', type='string', dest='target', default='/lustre/cmswork/zucchett/Ntuple/v0/weighted/')
parser.add_option('-f', '--filter', action='store', type='string', dest='filter', default='')
parser.add_option('-s', '--single', action='store_true', dest='single', default=False)
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)

(options, args) = parser.parse_args()

origin      = options.origin
target      = options.target
filterset   = options.filter
singlecore  = options.single
verbose     = options.verbose

LUMI    = 35867.

if not os.path.exists(origin):
    print 'Origin directory', origin, 'does not exist, aborting...'
    exit()
#if not os.path.exists(target):
#    print 'Target directory', target,'does not exist, aborting...'
#    exit()


##############################

def getSampleEvents(sample):
    if 'Run201' in sample: return 1.
    
    nEv = 0
    
    for f in os.listdir(origin + '/' + sample):
        tmpFile = TFile(origin + '/' + sample + '/' + f, 'READ')
        tmpHist = tmpFile.Get('Hists/Events')
        nEv += tmpHist.GetBinContent(1)
        tmpFile.Close()

    print sample, nEv, EV[sample]
#    print sample, LUMI*XS[sample]/nEv, LUMI*XS[sample]/EV[sample]
#    print sample, nEv/EV[sample]

def processFile(sample, filename):

    isMC = not 'Run201' in sample
    
    # Unweighted input
    ref_file_name = origin + '/' + sample + '/' + filename
    if not os.path.exists(ref_file_name): 
        print '  WARNING: file', ref_file_name, 'does not exist, continuing'
        return True
    
#    # Weighted output
#    new_file_name = target + '/' + sample + '/' + filename
#    if os.path.exists(new_file_name):
#        print '  WARNING: weighted file exists, overwriting'
#        #return True
#    
#    new_file = TFile(new_file_name, 'RECREATE')
#    new_file.cd()
    
    # Open old file
    ref_file = TFile(ref_file_name, 'READ')
    ref_hist = ref_file.Get('Events')
    try:
        totalEntries = ref_hist.GetBinContent(1)
    except:
        print '  ERROR: nEvents not found in file', sample
        exit(1)
        
    # Cross section
    XS = xsection[sample]['xsec']*xsection[sample]['kfactor']*xsection[sample]['br']
    Leq = LUMI*XS/totalEntries if totalEntries > 0 else 0.
    
    print sample, ": Leq =", (Leq if isMC else "Data")
    
    # Variables declaration
    stitchWeight = array('f', [1.0])
    eventWeightLumi = array('f', [1.0])  # global event weight with lumi
    
    # Looping over file content
    for key in ref_file.GetListOfKeys():
        obj = key.ReadObj()
        # Histograms
        if obj.IsA().InheritsFrom('TH1'):
            if verbose: print ' + TH1:', obj.GetName()
            new_file.cd()
            if isMC: obj.Scale(LUMI*XS/totalEntries)
            obj.Write()
        # Tree
        elif obj.IsA().InheritsFrom('TTree'):
            nev = obj.GetEntriesFast()
            new_file.cd()
            new_tree = obj.CopyTree("")
            # New branches
            stitchWeightBranch = new_tree.Branch('stitchWeight', stitchWeight, 'stitchWeight/F')
            eventWeightLumiBranch = new_tree.Branch('eventWeightLumi', eventWeightLumi, 'eventWeightLumi/F')

            # looping over events
            for event in range(0, obj.GetEntries()):
                if verbose and (event%10000==0 or event==nev-1): print ' = TTree:', obj.GetName(), 'events:', nev, '\t', int(100*float(event+1)/float(nev)), '%\r',
                #print '.',#*int(20*float(event)/float(nev)),#printProgressBar(event, nev)
                obj.GetEntry(event)
                # Initialize
                eventWeightLumi[0] = stitchWeight[0] = 1.
#                if obj.bTagWeight < 0.5 or obj.bTagWeight > 1.5: 
#                    print obj.bTagWeight
#                    print obj.Jet1_pt, obj.Jet2_pt, obj.Jet3_pt, obj.Jet4_pt
#                    print obj.Jet1_eta, obj.Jet2_eta, obj.Jet3_eta, obj.Jet4_eta
#                if obj.bTagWeight < 0.5: obj.bTagWeight = 0.5
#                if obj.bTagWeight > 1.5: obj.bTagWeight = 1.5
                # Weights
                if isMC:
                    # MC stitching
                    if sample=='DYJetsToLL' or sample=='WJetsToLNu' or sample=='W1JetsToLNu' or sample=='W2JetsToLNu' or sample=='W3JetsToLNu' or sample=='W4JetsToLNu':
                        if obj.LheHT > 70.: stitchWeight[0] = 0.
                    eventWeightLumi[0] = obj.eventWeight * obj.bTagWeight * obj.TopWeight
                    eventWeightLumi[0] *= LUMI*XS/totalEntries
                # Fill the branches
                stitchWeightBranch.Fill()
                eventWeightLumiBranch.Fill()

            new_file.cd()
            new_tree.Write("tree",TObject.kOverwrite)
            if verbose: print ' '
        
        # Directories
        elif obj.IsFolder():
            subdir = obj.GetName()
            if verbose: print ' \ Directory', subdir, ':'
            new_file.mkdir(subdir)
            new_file.cd(subdir)
            for subkey in ref_file.GetDirectory(subdir).GetListOfKeys():
                subobj = subkey.ReadObj()
                if subobj.IsA().InheritsFrom('TH1'):
                    if verbose: print '   + TH1:', subobj.GetName()
                    new_file.cd(subdir)
                    if isMC: subobj.Scale(LUMI*XS/totalEntries)
                    subobj.Write()
            new_file.cd('..')
        
    new_file.Close() 


singlecore = True
jobs = []
for s in os.listdir(origin):
    getSampleEvents(s)
#    for f in os.listdir(origin + '/' + s):
#        print s, f
#        if not '.root' in f: continue
#        if len(filterset)>0 and not filterset in s: continue
#        if singlecore:
#            print " -", d
#            processFile(s, f)
#        else:
#            p = multiprocessing.Process(target=processFile, args=(s, f,))
#            jobs.append(p)
#            p.start()
    #exit()
    
#print '\nDone.'

