#! /bin/usr/env bash
import os, re
from ROOT import TFile, TH2F #, TH2F, TGraphAsymmErrors, Double()
import numpy as np

def ensureTFile(filename,option='READ'):
  """Open TFile, checking if the file in the given path exists."""
  if not os.path.isfile(filename):
    print '>>> ERROR! DYCorrection.ensureTFile: File in path "%s" does not exist!!'%(filename)
    exit(1)
  file = TFile(filename,option)
  if not file or file.IsZombie():
    print '>>> ERROR! DYCorrection.ensureTFile Could not open file by name "%s"'%(filename)
    exit(1)
  return file
  


class DYCorrection:
    
    def __init__(self, name="<noname>"):
        self.name = name
        filename_qcd = "./CorrectionTools/DYCorrection/lindert_qcd_nnlo_sf.root"
        filename_ewk = "./CorrectionTools/DYCorrection/ewk_nlo_sf.root"
        self.file_qcd     = ensureTFile(filename_qcd)
        self.file_ewk     = ensureTFile(filename_ewk)
        if 'DYJetsToLL' in self.name:
          histname_qcd = "eej"
          histname_ewk = "z_ewkcorr/z_ewkcorr_func"
        elif 'ZJetsToNuNu' in self.name:
          histname_qcd = "vvj"
          histname_ewk = "z_ewkcorr/z_ewkcorr_func"
        elif 'WJetsToLNu' in self.name:
          histname_qcd = "evj"
          histname_ewk = "w_ewkcorr/w_ewkcorr_func"
        self.hist_qcd     = self.file_qcd.Get(histname_qcd)
        self.hist_qcd.SetDirectory(0)
        self.hist_ewk     = self.file_ewk.Get(histname_ewk)
        self.file_qcd.Close()
        self.file_ewk.Close()
        if 'DYJetsToLL' in self.name or 'ZJetsToNuNu' in self.name:
          self.a = 1.423
          self.b = 2.257
          self.c = 0.451
        elif 'WJetsToLNu' in self.name:
          self.a = 1.024
          self.b = 3.072
          self.c = 0.749
        self.getWeightQCDNLO = self.calculateWeight
        self.getWeightQCDNNLO = self.getWeightQCD
        self.getWeightEWKNLO = self.getWeightEWK

    def calculateWeight(self,pt):
      return self.a*np.exp(-self.b*pt/1000)+self.c
      
    def getWeightQCD(self,pt):
      bin = self.hist_qcd.GetXaxis().FindBin(pt)
      if bin==0: bin = 1
      elif bin>self.hist_qcd.GetXaxis().GetNbins() : bin -= 1
      weight = self.hist_qcd.GetBinContent(bin)
      if weight ==0: weight=1
      return weight
      
    def getWeightEWK(self,pt):
      return self.hist_ewk.Eval(pt)
  

