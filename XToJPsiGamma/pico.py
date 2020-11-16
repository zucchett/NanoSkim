#! /usr/bin/env python

import os, multiprocessing, math, datetime
from array import array
from ROOT import TFile, TH1, TF1, TLorentzVector, TObject

import optparse
usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--input', action='store', type='string', dest='origin', default='/lustre/cmsdata/zucchett/Higgs/v1/')
parser.add_option('-o', '--output', action='store', type='string', dest='target', default='/lustre/cmsdata/zucchett/Higgs/v1/Pico/')
parser.add_option('-f', '--filter', action='store', type='string', dest='filter', default='')
parser.add_option('-p', '--parallel', action='store_true', dest='parallel', default=False)
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)

(options, args) = parser.parse_args()

origin      = options.origin
target      = options.target
filterset   = options.filter
parallel    = options.parallel
verbose     = options.verbose


skimString = "isJPsiTrigger && nMuon >= 2 && nPhoton >= 1 && nCleanMuon == 0 && nCleanPhoton == 0 && nCleanElectron == 0 && Muon_pt[iMuon1] > 5. && Muon_pt[iMuon2] > 5. && Muon_mediumId[iMuon1] && Muon_mediumId[iMuon2] && minMuonIso < 0.05 && maxMuonIso < 0.15 && JPsi_pt > 26. && Photon_pt[iPhoton] > 15. && Photon_mvaID_WP80[iPhoton] && Photon_pfRelIso03_all[iPhoton] < 0.05 && H_dEta < 1.7 && nCleanJet <= 2 && (JPsi_mass > 3.0 && JPsi_mass < 3.2) && abs(Muon_dxy[iMuon1]-Muon_dxy[iMuon2])<0.015 && abs(Muon_dz[iMuon1]-Muon_dz[iMuon2])<0.020"

if not os.path.exists(origin):
    print '- Origin directory', origin, 'does not exist, aborting...'
    exit()
if not os.path.exists(target):
    print '- Target directory', target,'does not exist, aborting...'
    exit()


##############################

def skimTree(sample, filename):

    # Unweighted input
    inName = origin + '/' + sample + '/' + filename
    if not os.path.exists(inName): 
        print '- WARNING: file', inName, 'does not exist, continuing'
        return True
    
    # Weighted output
    if not os.path.exists(target + '/' + sample):
        os.mkdir(target + '/' + sample)
    
    outName = target + '/' + sample + '/' + filename
    if os.path.exists(outName):
        print '- WARNING: weighted file exists, overwriting'
        #return True
    
    outFile = TFile(outName, 'RECREATE')
    outFile.cd()
    
    # Open old file
    inFile = TFile(inName, 'READ')
    
    # Looping over file content
    for key in inFile.GetListOfKeys():
        obj = key.ReadObj()
        # Histograms
        if obj.IsA().InheritsFrom('TH1'):
            if verbose: print ' + TH1:', obj.GetName()
            outFile.cd()
            obj.Write()
        # Tree
        elif obj.IsA().InheritsFrom('TTree'):
            outFile.cd()
            newTree = obj.CopyTree(skimString if obj.GetName()=="Events" else "")
            ###
            absPhoton_eta = array('f', [1.0])
            absPhoton_etaBranch = newTree.Branch('absPhoton_eta', absPhoton_eta, 'absPhoton_eta/F')
            for event in range(0, obj.GetEntries()):
                obj.GetEntry(event)
                absPhoton_eta[0] = abs(obj.Photon_eta[obj.iPhoton]) if hasattr(obj, "Photon_eta") else -1.
                absPhoton_etaBranch.Fill()
            ###
            newTree.Write(obj.GetName(), TObject.kOverwrite)
            if verbose: print ' + TTree:', obj.GetName()
        # Directories
        elif obj.IsFolder():
            subdir = obj.GetName()
            if verbose: print ' \ Directory', subdir, ':'
            outFile.mkdir(subdir)
            outFile.cd(subdir)
            for subkey in inFile.GetDirectory(subdir).GetListOfKeys():
                subobj = subkey.ReadObj()
                if subobj.IsA().InheritsFrom('TH1'):
                    if verbose: print '   + TH1:', subobj.GetName()
                    outFile.cd(subdir)
                    subobj.Write()
            outFile.cd('..')
        
    outFile.Close() 



jobs = []

ncpu = multiprocessing.cpu_count() - 4 # Leave 4 CPU free
if parallel: print "+ Splitting jobs over", ncpu, "cores..."
pool = multiprocessing.Pool(processes = ncpu)
print "+ Job started [", datetime.datetime.now().time(), "]"

for s in os.listdir(origin):
    if len(filterset)>0 and not filterset in s: continue
    for f in os.listdir(origin + '/' + s):
        if not '.root' in f: continue
        if not parallel:
            print "+ ", s, f
            skimTree(s, f)
        else:
            #p = multiprocessing.Process(target=skimTree, args=(s, f,))
            #jobs.append(p)
            #p.start()
            pool.apply_async(skimTree, args=(s, f,))

# Wait for all jobs to finish
pool.close()
pool.join()
print "+ Jobs completed [", datetime.datetime.now().time(), "]"            

print '\nDone.'


# python pico.py -p -i /lustre/cmsdata/zucchett/Higgs/v1/ -o /lustre/cmsdata/zucchett/Higgs/v1/Pico/

