# NanoSkim general information

The events are categorized according to the following exclusive selections. The categories are exclusive and ordered giving priority to final states with multileptons (3, 4, 1, 2, 5, 6)

## Skim categories

* **iSkim=1** ***(2 muons)***
  - the SingleMuIsoTrigger or SingleMuTrigger
  - leading muon with pT > 27 GeV
  - second muon with pT > 7 GeV
  - both muons passing the `medium` id
  - dimuon invariant mass > 15 GeV
  - no requirement of muon sign

* **iSkim=2** ***(1 muon 1 electron)***
  - the SingleMuIsoTrigger or SingleMuTrigger
  - leading muon with pT > 27 GeV
  - leading electron with pT > 20 GeV
  - leading muon passing the `medium` id
  - leading electron passing the `medium` wp (`Electron_cutBased >= 2`)
  - muon-electron invariant mass > 15 GeV
  
* **iSkim=3** ***(3 muons)***
  - the SingleMuIsoTrigger or SingleMuTrigger
  - leading muon with pT > 27 GeV
  - second muon with pT > 15 GeV
  - second muon with pT > 15 GeV
  - all 3 muons passing the `medium` id
  - Z candidate reconstructed from the OS muon pair with highest muon pT
  - dimuon invariant mass > 15 GeV

* **iSkim=4** ***(2 muons, 1 electron)***
  - the SingleMuIsoTrigger or SingleMuTrigger
  - leading muon with pT > 27 GeV
  - second muon with pT > 15 GeV
  - leading electron with pT > 15 GeV
  - both muons passing the `medium` id
  - leading electron passing the `medium` wp (`Electron_cutBased >= 2`)
  - the 2 muons have opposite sign
  - dimuon invariant mass > 15 GeV

* **iSkim=5** ***(1 iso muon, 3 jets, 1 btag)***
  - the SingleMuIsoTrigger or SingleMuTrigger
  - leading muon with pT > 27 GeV
  - leading muon passing the `medium` id
  - leading muon loosely isolated (`Muon_pfRelIso03_all < 0.15`)
  - at least 3 jets with pT > 30 GeV
  - at least one jet b-tagged with the `DeepCSV` `medium` working point

* **iSkim=6** ***(2 electrons)***
  - the SingleEleIsoTrigger
  - leading electron with pT > 35 GeV
  - second electron with pT > 20 GeV
  - both electrons passing the `loose` wp (`Electron_cutBased >= 1`)
  - dielectron ivariant mass > 15 GeV

