#! /usr/bin/env python

alias = {
    "Pre" : "iSkim>0",
    "Z2mCR" : "iSkim==1 && isSingleMuIsoTrigger && Muon_charge[0]*Muon_charge[1]<0 && Muon_pfRelIso03_all[0]<0.10 && Muon_pfRelIso03_all[1]<0.10 && Z_mass > 60 && Z_mass < 120",
    "T2lCR" : "iSkim==2 && isSingleMuIsoTrigger && Electron_pt[0]>20. && Muon_charge[0]*Electron_charge[0]<0 && Muon_pfRelIso03_all[0]<0.10",
    "VV3mCR" : "iSkim==3 && isSingleMuIsoTrigger && Muon_pt[1]>20. && Muon_pt[2]>20. && Muon_pfRelIso03_all[0]<0.10 && Muon_pfRelIso03_all[1]<0.10 && Muon_pfRelIso03_all[2]<0.10",
    "VV2meCR" : "iSkim==4 && isSingleMuIsoTrigger && Muon_pt[1]>20. && Electron_pt[0]>20. && Muon_pfRelIso03_all[0]<0.10 && Muon_pfRelIso03_all[1]<0.10",
    "T1mCR" : "iSkim==5 && isSingleMuIsoTrigger && Muon_pt[0]>40. && Muon_pfRelIso03_all[0]<0.10 && nCleanMuon==1 && minMuonJetDR>0.5 && W_tmass>40.",
    "Z2eCR" : "iSkim==6 && isSingleEleIsoTrigger && Electron_charge[0]*Electron_charge[1]<0 && Z_mass > 60 && Z_mass < 120",
    "ZgCR" : "iSkim==1 && isSingleMuIsoTrigger && Muon_charge[0]*Muon_charge[1]<0 && Muon_pfRelIso03_all[0]<0.10 && Muon_pfRelIso03_all[1]<0.10 && Z_mass > 60 && Z_mass < 120 && Photon_pt[0]>-15. && Photon_pfRelIso03_all[0]<0.10 && Photon_mvaID_WP80[0]",
}

aliasNames = {
    "Pre" : "Preselection",
    "Z2mCR" : "2#mu control region",
    "T2lCR" : "1#mu, 1e control region",
    "VV3mCR" : "3#mu control region",
    "VV2meCR" : "2#mu, 1e control region",
    "T1mCR" : "1#mu, t#bar{t} control region",
    "ZgCR" : "2#mu+#gamma control region",
}
