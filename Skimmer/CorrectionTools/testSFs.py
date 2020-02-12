#! /usr/bin/env python
# Author: Izaak Neutelings (December 2018)

import time
start0 = time.time()
print
print ">>> importing modules..."
import os; os.chdir('..')

start1 = time.time()
from ROOT import TFile
print ">>>   imported ROOT classes after %.1f seconds"%(time.time()-start1)

start1 = time.time()
from ScaleFactorTool import *
print ">>>   imported ScaleFactorTool classes after %.1f seconds"%(time.time()-start1)

start1 = time.time()
from MuonSFs import *
print ">>>   imported MuonSFs classes after %.1f seconds"%(time.time()-start1)

start1 = time.time()
from ElectronSFs import *
print ">>>   imported ElectronSFs classes after %.1f seconds"%(time.time()-start1)

start1 = time.time()
from BTaggingTool import *
print ">>>   imported BTagWeightTool classes after %.1f seconds"%(time.time()-start1)
print ">>>   imported everything after %.1f seconds"%(time.time()-start0)
print ">>> "

# PATHS
path       = 'CorrectionTools/leptonEfficiencies/'
pathHTT_mu = 'CorrectionTools/leptonEfficiencies/HTT/Muon/Run2017/'
pathHTT_el = 'CorrectionTools/leptonEfficiencies/HTT/Electron/Run2017/'

# PT & ETA
ptvals  = [ 10., 20., 21., 22., 24., 26., 27., 34., 35., 36., 40., 60., 156., 223., 410., 560. ]
etavals = [ 0.0, 0.5, 1.1, 1.9, 2.0, 2.3, 2.4, 2.8, 3.4 ]
etavals = [-eta for eta in reversed(etavals)]+etavals
points  = [ ]
for pt in ptvals:
  for eta in etavals:
    #points.append((pt,-eta))
    points.append((pt,eta))



def printMatrix(name,method):
  start2 = time.time()
  print ">>>   %s:"%name
  print ">>>    %10s"%('pt\eta')+' '.join('%10.2f'%eta for eta in etavals)
  for pt in ptvals:
    print ">>>    %10.2f"%(pt)+' '.join('%10.3f'%method(pt,eta) for eta in etavals)
  print ">>>   got %d SFs in %.3f seconds"%(len(ptvals)*len(etavals),time.time()-start2)
  print ">>> "
  

def muonPOG():
  
  # TRIGGER (Muon POG)
  start1 = time.time()
  print ">>> initializing trigger SFs from Muon POG..."
  sftool_trig = ScaleFactor(path+"MuonPOG/Run2017/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root","IsoMu27_PtEtaBins/abseta_pt_ratio",'mu_trig',ptvseta=True)
  print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  printMatrix('trigger POG',sftool_trig.getSF)
  
  # ID (Muon POG)
  start1 = time.time()
  sftool_id  = ScaleFactor(path+"MuonPOG/Run2018/RunABCD_SF_ID.root","NUM_MediumID_DEN_genTracks_pt_abseta",'mu_id',ptvseta=False)
  print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  printMatrix('id POG',sftool_id.getSF)
  
  # ISO (Muon POG)
  start1 = time.time()
  sftool_iso = ScaleFactor(path+"MuonPOG/Run2018/RunABCD_SF_ISO.root","NUM_TightRelIso_DEN_MediumID_pt_abseta",'mu_iso',ptvseta=False)
  print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  printMatrix('iso POG',sftool_iso.getSF)
  
  # ID/ISO (Muon POG)
  start1 = time.time()
  sftool_idiso    = sftool_id*sftool_iso
  print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  printMatrix('idiso POG',sftool_idiso.getSF)  
  print ">>> "
  

def muonHTT():
  
  # TRIGGER (HTT)
  start1 = time.time()
  print ">>> initializing trigger SFs from HTT..."
  sftool_mu_trig_HTT = ScaleFactorHTT(pathHTT_mu+"Muon_IsoMu24orIsoMu27.root","ZMass",'mu_idiso')
  print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  printMatrix('trigger HTT',sftool_mu_trig_HTT.getSF)
  
  ## ID ISO (HTT)
  #start1 = time.time()
  #print ">>> initializing idiso SFs from HTT..."
  #sftool_mu_idiso_HTT = ScaleFactorHTT(pathHTT_mu+"Muon_IdIso_IsoLt0p15_eff_RerecoFall17.root","ZMass",'mu_idiso')
  #print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  #printMatrix('idiso HTT',sftool_mu_idiso_HTT.getSF)
  #print ">>> "
  

def electronHTT():
  
  # RECO (EGAMMA POG)
  sftool_ele_reco_HTT = ScaleFactor(pathHTT_el+"egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root","EGamma_SF2D",'ele_reco',ptvseta=True)
  printMatrix('reco POG',sftool_ele_reco_HTT.getSF)
  
  # ID/ISO (HTT)
  sftool_ele_idiso_HTT = ScaleFactorHTT(pathHTT_el+"Electron_IdIso_IsoLt0.15_IsoID_eff.root","ZMass",'ele_idiso')
  printMatrix('idiso HTT',sftool_ele_idiso_HTT.getSF)
  

def muonSFs():
  
  # MUON SFs
  start1 = time.time()
  print ">>> initializing MuonSF object..."
  muSFs = MuonSFs()
  print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  
  # GET SFs
  printMatrix('trigger',muSFs.getTriggerSF)
  printMatrix('idiso',muSFs.getIdIsoSF)
  print ">>> "
  
  # MUON 2018 SFs
  start1 = time.time()
  print ">>> initializing MuonSF(2018) object..."
  muSFs = MuonSFs(year=2018)
  print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  
  # GET SFs
  printMatrix('trigger',muSFs.getTriggerSF)
  printMatrix('idiso',muSFs.getIdIsoSF)
  print ">>> "
  

def electronSFs():
  
  # ELECTRON SFs
  print ">>> "
  start1 = time.time()
  print ">>> initializing ElectronSFs object..."
  eleSFs = ElectronSFs()
  print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  
  # GET SFs
  printMatrix('trigger',eleSFs.getTriggerSF)
  printMatrix('idiso',eleSFs.getIdIsoSF)
  

def btagSFs(tagger='CSVv2'):
  
  # BTAG SFs
  print ">>> "
  start1 = time.time()
  print ">>> initializing BTagWeightTool(%s) object..."%tagger
  btagSFs = BTagWeightTool(tagger)
  print ">>>   initialized in %.1f seconds"%(time.time()-start1)
  
  # GET SFs
  printMatrix('%s g'%tagger,lambda p,e: btagSFs.getSF(p,e,0))
  #printMatrix('%s u'%tagger,lambda p,e: btagSFs.getSF(p,e,1))
  #printMatrix('%s d'%tagger,lambda p,e: btagSFs.getSF(p,e,2))
  #printMatrix('%s s'%tagger,lambda p,e: btagSFs.getSF(p,e,3))
  printMatrix('%s c'%tagger,lambda p,e: btagSFs.getSF(p,e,4))
  printMatrix('%s b'%tagger,lambda p,e: btagSFs.getSF(p,e,5))
  

if __name__ == "__main__":
  
  muonPOG()
  #muonHTT()
  #electronHTT()
  #muonSFs()
  #electronSFs()
  #btagSFs('CSVv2')
  #btagSFs('DeepCSV')
  print ">>> "
  print ">>> done after %.1f seconds"%(time.time()-start0)
  print
