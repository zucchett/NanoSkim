# Correction Tools
Several tools to get corrections, efficiencies, scale factors (SFs), event weights, etc.



## Pileup reweighting

`PileupWeightTool.py` provides the pileup event weight based on the data and MC profiles in [`pileup/`](https://github.com/IzaakWN/NanoTreeProducer/tree/master/CorrectionTools/pileup).

The data profile can be computed with the `brilcalc` tool on `lxplus`.
The MC profile can be taken from the distribution of the `Pileup_nTrueInt` variable in nanoAOD, for each MC event:
```
    self.out.pileup.Fill(event.Pileup_nTrueInt)
```
and then extracted with [`pileup/getPileupProfiles.py`](https://github.com/IzaakWN/NanoTreeProducer/blob/master/CorrectionTools/pileup/getPileupProfiles.py). Comparisons are shown [here for 2017](https://ineuteli.web.cern.ch/ineuteli/pileup/2017/) and [here for 2018](https://ineuteli.web.cern.ch/ineuteli/pileup/2018/).



## Lepton efficiencies

Several classes are available to get corrections for electrons, muons and hadronically-decayed tau leptons:

* `ScaleFactorTool.py`
  * `ScaleFactor`: general class to get SFs from histograms
  * `ScaleFactorHTT`: class to get SFs from histograms, as measured by the [HTT group](https://github.com/CMS-HTT/LeptonEfficiencies)
* `MuonSFs.py`: class to get muon trigger / identification / isolation SFs
* `ElectronSFs.py` class to get electron trigger / identification / isolation SFs
* `TauTauSFs.py` class to get ditau trigger SFs
* `LeptonTauFakeSFs.py` class to get lepton to tau fake SFs

`ROOT` files with efficiencies and SFs are saved in [`leptonEfficiencies`](https://github.com/IzaakWN/NanoTreeProducer/blob/master/CorrectionTools/leptonEfficiencies). In case you use lepton scale factors and efficiencies from the HTT group, you need to make sure you get them:
```
cd leptonEfficiencies
git clone https://github.com/CMS-HTT/LeptonEfficiencies HTT
```



## B-tagging tools

`BTaggingTool.py` provides two classes: `BTagWPs` for saving the working points (WPs) per year and type of tagger, and `BTagWeightTool` to provide b-tagging weights. These can be called during the initialization of you analysis module, e.g. in [`MuTauModule.py`](https://github.com/IzaakWN/NanoTreeProducer/blob/master/MuTauModule.py):
```
class MuTauProducer(Module):
    
    def __init__(self, ... ):
        
        ...
        
        if not self.isData:
          self.btagTool = BTagWeightTool('DeepCSV','medium',channel=channel,year=year)
        self.deepcsv_wp = BTagWPs('DeepCSV',year=year)
        
    
    def analyze(self, event):
        
        nbtag  = 0
        jetIds = [ ]
        for ijet in range(event.nJet):
            ...
            jetIds.append(ijet)
            if event.Jet_btagDeepB[ijet] > self.deepcsv_wp.medium:
              nbtag += 1
        
        if not self.isData:
          self.out.btagweight[0] = self.btagTool.getWeight(event,jetIds)
```

`BTagWeightTool` calculates b-tagging reweighting based on the [SFs provided from the BTagging group](https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation#Recommendation_for_13_TeV_Data) and analysis-dependent efficiencies measured in MC. These are saved in `ROOT` files in [`btag/`](https://github.com/IzaakWN/NanoTreeProducer/tree/master/CorrectionTools/btag).
The event weight is calculated according to [this method](https://twiki.cern.ch/twiki/bin/viewauth/CMS/BTagSFMethods#1a_Event_reweighting_using_scale).

The efficiencies in MC can be calculated for your particular analys by filling histograms with `fillEfficiencies` for each selected event, after removing overlap with other selected objects, e.g. the muon and tau object in [`MuTauModule.py`](https://github.com/IzaakWN/NanoTreeProducer/blob/master/MuTauModule.py):
<pre>
    def analyze(self event):
    
        # select isolated muon and tau
        ...
        
        for ijet in range(event.nJet):
            if event.Jet_pt[ijet] < 30: continue
            if abs(event.Jet_eta[ijet]) > 4.7: continue
            <b>if muon.DeltaR(jets[ijet].p4()) < 0.5: continue
            if tau.DeltaR(jets[ijet].p4()) < 0.5: continue</b>
            jetIds.append(ijet)
        
        if not self.isData:
          self.btagTool.fillEfficiencies(event,jetIds)
        
        ...
</pre>
Then use [`btag/getBTagEfficiencies.py`](https://github.com/IzaakWN/NanoTreeProducer/blob/master/CorrectionTools/btag/getBTagEfficiencies.py) to extract all histograms from MC output and compute the efficiencies. Examples for the mutau analysis in 2017 are shown [here](https://ineuteli.web.cern.ch/ineuteli/btag/2017/).



## Recoil corrections

`RecoilCorrectionTool.py` provides the tools for three different things:
* **Z pT reweighting** of LO Drell-Yan events as a function of Z boson pT and mass:
  * `getZBoson`: compute the (full) Z boson's four-vector from its daugher leptons,
  * `RecoilCorrectionTool.getZptWeight`: get weights are stored in [`Zpt/`](https://github.com/IzaakWN/NanoTreeProducer/tree/master/CorrectionTools/Zpt).
* **Top pT reweighting** of ttbar events as a function of the pT of both top quarks:
  * `getTTPt`: compute the generator-level top pT's,
  * `getTTptWeight`: get [SFs recommended by Top PAG](https://twiki.cern.ch/twiki/bin/view/CMS/TopPtReweighting).
* [**Recoil corrections** to the MET](https://github.com/CMS-HTT/RecoilCorrections/blob/master/instructions.txt) for W/Z/Higgs events (see HTT's [AN-2016/355](http://cms.cern.ch/iCMS/user/noteinfo?cmsnoteid=CMS%20AN-2016/355)):
  * `getBoson`: compute the full and visible four-vector of the Z/W/Higgs boson at generator-level [[recommendation](https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsToTauTauWorking2016#Recoil_corrections)],
  * `RecoilCorrectionTool.CorrectPFMETByMeanResolution`: apply the correction to a given MET four-vector.

Usage:
```
    def analyze(self event):
        
        met = ROOT.TLorentzVector()
        met.SetPxPyPzE(event.MET_pt*math.cos(event.MET_phi),event.MET_pt*math.cos(event.MET_phi),0,event.MET_pt)
        if Z/W/Higgs event:
          boson, boson_vis = getBoson(event)
          self.recoilTool.CorrectPFMETByMeanResolution(met,boson,boson_vis,event.nJet)
          event.MET_pt     = met.Pt()
          event.MET_phi    = met.Phi()
        
        if Z event:
          zboson = getZBoson(event)
          zptweight = self.recoilTool.getZptWeight(boson.Pt(),boson.M())          
        
        if ttbar event:
          toppt1, toppt2   = getTTPt(event)
          ttptweight       = getTTptWeight(toppt1,toppt2)
```
Note that `zboson` and `boson` are equivalent.


## Test SFs

`testSFs.py` provides a simple and direct way of testing the correction tool classes, without running the whole framework.


