#! /usr/bin/env python

import os, multiprocessing, math
from array import array
from ROOT import TFile, TTree, TH1, TLorentzVector, TObject

########## SAMPLES ##########
data = ["data_obs"]
back = ["VV", "TTbar", "DYJetsToLL"]
#back = ["VV", "ST", "TTbarSL", "WJetsToLNu_HT", "DYJetsToNuNu_HT", "DYJetsToLL_HT"] #, "QCD"]
sign = []
variables = ["Z_mass", "Z_pt", "Muon_pt[0]"]
categories = ["Z2mCR"]
########## ######## ##########



# Loop on events
def loop(hist, tree, red):
    nev = tree.GetEntries()
    for event in range(0, nev, red):
        tree.GetEntry(event)
        weight = tree.eventWeightLumi * red
        # Z2mCR selection
        if tree.iSkim==1 and tree.isSingleMuIsoTrigger and tree.Muon_charge[0]*tree.Muon_charge[1]<0 and tree.Muon_pfRelIso03_all[0]<0.10 and tree.Muon_pfRelIso03_all[1]<0.10 and tree.Z_mass > 60 and tree.Z_mass < 120:
            m1, m2 = TLorentzVector(), TLorentzVector()
            m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
            m2.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
            mll = (m1+m2).M()
            hist["Z2mCR"]["Z_mass"].Fill((m1+m2).M(), weight)
            hist["Z2mCR"]["Z_pt"].Fill((m1+m2).Pt(), weight)
            hist["Z2mCR"]["Muon_pt[0]"].Fill(tree.Muon_pt[0], weight)
    return
