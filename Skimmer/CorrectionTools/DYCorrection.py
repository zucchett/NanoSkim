#! /bin/usr/env bash
import os, re
from ROOT import TFile, TLorentzVector, TH2F #, TH2F, TGraphAsymmErrors, Double()
import numpy as np

from global_paths import MAINDIR
path = MAINDIR + 'CorrectionTools/DYCorrection/'

def ensureTFile(filename,option='READ'):
  """Open TFile, checking if the file in the given path exists."""
  if not os.path.isfile(filename):
    print '- ERROR! DYCorrection.ensureTFile: File in path "%s" does not exist!!'%(filename)
    exit(1)
  file = TFile(filename,option)
  if not file or file.IsZombie():
    print '- ERROR! DYCorrection.ensureTFile Could not open file by name "%s"'%(filename)
    exit(1)
  return file
  


class DYCorrection:
    
    def __init__(self, name="<noname>"):
        self.name = name
        filename_qcd = path + "lindert_qcd_nnlo_sf.root"
        filename_ewk_zjets = path +"merged_kfactors_zjets.root"
        filename_ewk_wjets = path + "merged_kfactors_wjets.root"
        self.file_qcd     = ensureTFile(filename_qcd)
        histname_ewk = "kfactor_monojet_ewk"
        if 'DYJetsToLL' in self.name:
          histname_qcd = "eej"
          self.file_ewk = ensureTFile(filename_ewk_zjets)
        elif 'ZJetsToNuNu' in self.name:
          histname_qcd = "vvj"
          self.file_ewk = ensureTFile(filename_ewk_zjets)
        elif 'WJetsToLNu' in self.name:
          histname_qcd = "evj"
          self.file_ewk = ensureTFile(filename_ewk_wjets)
        self.hist_qcd     = self.file_qcd.Get(histname_qcd)
        self.hist_qcd.SetDirectory(0)
        self.hist_ewk = self.file_ewk.Get(histname_ewk)
        self.hist_ewk.SetDirectory(0)
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
      bin = self.hist_ewk.GetXaxis().FindBin(pt)
      if bin==0: bin = 1
      elif bin>self.hist_ewk.GetXaxis().GetNbins() : bin -= 1
      weight = self.hist_ewk.GetBinContent(bin)
      if weight ==0: weight=1
      return weight
  
    def getGenVpt(self,event):
      GenVpt = 0.
      VPt = -1.
      idx_V = -1
      LepP = TLorentzVector()
      LepM = TLorentzVector()
      particle_masses = {11 : 0.000511,
                         12 : 0.,
                         13 : 0.10566,
                         14 : 0.,
                         15 : 1.77686, 
                         16 : 0.}
      
      for idx_gen in range(event.nGenPart):
        if event.GenPart_pdgId[idx_gen] == 23 or event.GenPart_pdgId[idx_gen] == 24:
          if VPt<=0.:
            VPt = event.GenPart_pt[idx_gen]
            idx_V = idx_gen
          else:
            if event.GenPart_genPartIdxMother[idx_gen]==idx_V:
              VPt = event.GenPart_pt[idx_gen]
              idx_V = idx_gen
        elif (event.GenPart_status[idx_gen]==1 and event.GenPart_pdgId[idx_gen] >= +11 and event.GenPart_pdgId[idx_gen] <= +16)  or (event.GenPart_pdgId[idx_gen]== +15 and event.GenPart_status[idx_gen]==2):
          if event.GenPart_pt[idx_gen]>LepP.Pt():
            particle_mass = particle_masses[abs(event.GenPart_pdgId[idx_gen])]
            LepP.SetPtEtaPhiM(event.GenPart_pt[idx_gen],event.GenPart_eta[idx_gen],event.GenPart_phi[idx_gen],particle_mass)
        elif (event.GenPart_status[idx_gen]==1 and event.GenPart_pdgId[idx_gen] >= -16 and event.GenPart_pdgId[idx_gen] <= -11) or (event.GenPart_pdgId[idx_gen]== -15 and event.GenPart_status[idx_gen]==2):
          if event.GenPart_pt[idx_gen]>LepM.Pt():
            particle_mass = particle_masses[abs(event.GenPart_pdgId[idx_gen])]
            LepM.SetPtEtaPhiM(event.GenPart_pt[idx_gen],event.GenPart_eta[idx_gen],event.GenPart_phi[idx_gen],particle_mass)
      if VPt > 0.:
        GenVpt = VPt
      elif LepP.Pt() > 0. and LepM.Pt() > 0.:
        GenVpt = (LepP+LepM).Pt()
      return GenVpt

