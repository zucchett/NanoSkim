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


## Run on LSF

In order to run on nanoAOD files not stored on the Legnaro T2, the file prefix to prepend to the file name should be adjusted in `global_paths.py`. Additionally, in order to make the proxy visible when running on the LSF nodes, manually copy the proxy in the local directory on `/lustre`. The proxy location is reported each time the proxy is created and it is usually in `/tmp/x509up_u723`. Remember to update the path to this file in `global_paths.py`.


## Add new samples

First, make sure to login to the grid: `voms-proxy-init --voms cms --valid 168:00`

1. Add the full path of the new files on `fileList_*.txt`, as taken from DAS.

2. Create file list: `python lists.py`.  The option `-f` specifies a string to filter the samples.

3. Count events to determine the normalization: `python events.py`.  The option `-f` specifies a string to filter the samples. At the moment, the dictionary is printed to screen and should be checked manually before copying the number of events to the dictionary `EV` in `utils.py`.

4. Report the cross sections in `utils.py` in the appropriate dictionary `XS`, by using the same keys as for the events number. Copy the same keys in an ordered manner in the `SAMPLES` list.

5. Make sure that the target and work directories are empty. Then submit the jobs with `python submitSkim.py`. The option `-f` specifies a string to filter the samples.


