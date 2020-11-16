#! /usr/bin/env python

alias = {
    "MuonGang" : "isSingleMuonPhotonTrigger && nMuon >= 2 && nPhoton >= 1 && Muon_pt[iMuon1] > 28. && Muon_pt[iMuon2] > 10. && Muon_looseId[iMuon1] && Muon_looseId[iMuon2] && Muon_pfRelIso03_all[iMuon1] < 0.15 && Muon_pfRelIso03_all[iMuon2] < 0.15 && Photon_pt[iPhoton] > 25. && Photon_mvaID_WP80[iPhoton] && Photon_pfRelIso03_all[iPhoton] < 0.15", 
    "PreAltTrig" : "isSingleMuonPhotonTrigger && nMuon >= 2 && nPhoton >= 1 && nCleanMuon == 0 && nCleanPhoton == 0 && nCleanElectron == 0 && Muon_pt[iMuon1] > 18. && Muon_pt[iMuon2] > 5. && Muon_mediumId[iMuon1] && Muon_mediumId[iMuon2] && minMuonIso < 0.05 && maxMuonIso < 0.15 && Photon_pt[iPhoton] > 32. && Photon_mvaID_WP80[iPhoton] && Photon_pfRelIso03_all[iPhoton] < 0.05",
    "Preselection" : "isJPsiTrigger && nMuon >= 2 && nPhoton >= 1 && nCleanMuon == 0 && nCleanPhoton == 0 && nCleanElectron == 0 && Muon_pt[iMuon1] > 5. && Muon_pt[iMuon2] > 5. && Muon_mediumId[iMuon1] && Muon_mediumId[iMuon2] && minMuonIso < 0.05 && maxMuonIso < 0.15 && JPsi_pt > 26. && Photon_pt[iPhoton] > 15. && Photon_mvaID_WP90[iPhoton] && Photon_pfRelIso03_all[iPhoton] < 0.15",
}

alias["SR"] = alias["Preselection"] + " && (JPsi_mass > 3.0 && JPsi_mass < 3.2) && abs(Muon_dxy[iMuon1]-Muon_dxy[iMuon2])<0.015 && abs(Muon_dz[iMuon1]-Muon_dz[iMuon2])<0.02"
alias["Barrel"] = alias["SR"] + " && abs(Photon_eta[iPhoton]) < 1.479"
alias["Endcap"] = alias["SR"] + " && abs(Photon_eta[iPhoton]) > 1.653"


aliasNames = {
    "Default" : "Default",
    "MuonGang" : "MuonGang",
    "Preselection" : "Preselection",
    "PreAltTrig" : "Preselection (single #mu+#gamma trigger)",
    "SR" : "Signal Region",
    "Barrel" : "Barrel",
    "Endcap" : "Endcaps",
}
