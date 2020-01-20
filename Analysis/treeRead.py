#! /usr/bin/env python

import os, multiprocessing, math
from array import array
from ROOT import TFile, TH1F, TF1, TLorentzVector, TObject

cut = "eventWeightLumi*(iSkim==1 && isSingleMuIsoTrigger && Muon_charge[0]*Muon_charge[1]<0 && Muon_pfRelIso03_all[0]<0.10 && Muon_pfRelIso03_all[1]<0.10 && Z_mass > 60 && Z_mass < 120)"

def count(sample):
    n = 0
    for f in os.listdir(sample):
        tmpFile = TFile(sample + '/' + f, 'READ')
#        tmpHist = tmpFile.Get('Hists/Events')
        tree = tmpFile.Get("Events")
        tmpHist = TH1F(f, "", 1, -999999999., 99999999.)
        tree.Project(f, "iSkim", cut)
        n += tmpHist.GetBinContent(1)
        tmpFile.Close()
    print sample, n
    return n


N = 0
N += count("/lustre/cmswork/zucchett/Ntuple/v0/SingleMuon_Run2016B_ver1-Nano1June2019_ver1-v1/")
N += count("/lustre/cmswork/zucchett/Ntuple/v0/SingleMuon_Run2016B_ver2-Nano1June2019_ver2-v1/")
N += count("/lustre/cmswork/zucchett/Ntuple/v0/SingleMuon_Run2016C-Nano1June2019-v1/")
N += count("/lustre/cmswork/zucchett/Ntuple/v0/SingleMuon_Run2016D-Nano1June2019-v1")
N += count("/lustre/cmswork/zucchett/Ntuple/v0/SingleMuon_Run2016E-Nano1June2019-v1/")
N += count("/lustre/cmswork/zucchett/Ntuple/v0/SingleMuon_Run2016F-Nano1June2019-v1/")
N += count("/lustre/cmswork/zucchett/Ntuple/v0/SingleMuon_Run2016G-Nano1June2019-v1/")
N += count("/lustre/cmswork/zucchett/Ntuple/v0/SingleMuon_Run2016H-Nano1June2019-v1/")
print "data:", N

DY = count("DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISummer16/")
print "DY:", DY


#-bash-4.1$ python plot.py -v iSkim -c ZmmCR -b
#Sample                  Events          Entries         %
#------------------------------------------------------------
#data_obs             	16777216.00 	24561465   	89.75     
#------------------------------------------------------------
#TTbar                	91126.30   	1911205    	0.49      
#DYJetsToLL           	18599436.00 	14234269   	99.49     
#VV                   	3521.86    	437117     	0.02      
#------------------------------------------------------------
#BkgSum               	18694084.00 	16582593   	100.00    
#------------------------------------------------------------
#------------------------------------------------------------











