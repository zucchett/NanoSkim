from ScaleFactorTool import ScaleFactor

# /shome/ytakahas/work/Leptoquark/CMSSW_9_4_4/src/PhysicsTools/NanoAODTools/NanoTreeProducer/leptonSF
# HTT: https://github.com/CMS-HTT/LeptonEfficiencies
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2017
# https://twiki.cern.ch/twiki/bin/view/CMS/Egamma2017DataRecommendations#Efficiency_Scale_Factors
from global_paths import MAINDIR
path    = MAINDIR + 'CorrectionTools/leptonEfficiencies/MuonPOG/'

class MuonSFs:
    
    def __init__(self, year=2017):
        """Load histograms from files."""
        assert year in [2016,2017,2018], "MuonSFs: You must choose a year from: 2016, 2017 or 2018."
        self.year = year
        if year==2016:
            self.sftool_trig  = ScaleFactor(path+"Run2016/SingleMuonTrigger_2016.root","IsoMu24_OR_IsoTkMu24_PtEtaBins/abseta_pt_ratio","mu_trig") #Mu50_OR_TkMu50_PtEtaBins
            self.sftool_id    = ScaleFactor(path+"Run2016/RunBCDEF_SF_ID.root","NUM_MediumID_DEN_genTracks_eta_pt","mu_id") #NUM_HighPtID_DEN_genTracks_eta_pair_newTuneP_probe_pt\
            self.sftool_iso   = ScaleFactor(path+"Run2016/RunBCDEF_SF_ISO.root","NUM_LooseRelIso_DEN_MediumID_eta_pt","mu_iso")
            self.sftool_trkid = ScaleFactor(path+"Run2016/trackHighPtID_effSF_80X.root","sf_trackHighPt_80X_pteta","mu_trkid")
        elif year==2017:
            self.sftool_trig  = ScaleFactor(path+"Run2017/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root","Mu50_PtEtaBins/abseta_pt_ratio",'mu_trig')
            self.sftool_id    = ScaleFactor(path+"Run2017/RunBCDEF_SF_ID.root","NUM_HighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta",'mu_id',ptvseta=False)
            self.sftool_iso   = ScaleFactor(path+"Run2017/RunBCDEF_SF_ISO.root","NUM_LooseRelIso_DEN_MediumID_pt_abseta",'mu_iso',ptvseta=False)
            self.sftool_trkid = ScaleFactor(path+"Run2017/RunBCDEF_SF_ID.root","NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta",'mu_trkid',ptvseta=False)
        elif year==2018:
            self.sftool_trig  = ScaleFactor(path+"Run2018/EfficienciesAndSF_2018Data_AfterMuonHLTUpdate.root","Mu50_OR_OldMu100_OR_TkMu100_PtEtaBins/abseta_pt_ratio",'mu_trig')
            self.sftool_id    = ScaleFactor(path+"Run2018/RunABCD_SF_ID.root","NUM_HighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta",'mu_id',ptvseta=False)
            self.sftool_iso   = ScaleFactor(path+"Run2018/RunABCD_SF_ISO.root","NUM_LooseRelIso_DEN_MediumID_pt_abseta",'mu_id',ptvseta=False)
            self.sftool_trkid = ScaleFactor(path+"Run2018/RunABCD_SF_ID.root","NUM_TrkHighPtID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta",'mu_trkid',ptvseta=False)


        
    def getTriggerSF(self, pt, eta):
        """Get SF for single muon trigger."""
        return self.sftool_trig.getSF(pt,abs(eta))
    
    def getTriggerSFerror(self, pt, eta):
        """Get SF for single muon trigger."""
        return self.sftool_trig.getSFerror(pt,abs(eta))

    
    def getIdSF(self, pt, eta, highptid):
        """Get SF for muon identification + isolation."""
        if highptid==1:
            return self.sftool_trkid.getSF(pt,abs(eta))
        elif highptid==2:
            return self.sftool_id.getSF(pt,abs(eta))
        else:
            return 1.

    def getIdSFerror(self, pt, eta, highptid):
        """Get SF for muon identification + isolation."""
        if highptid==1:
            return self.sftool_trkid.getSFerror(pt,abs(eta))
        elif highptid==2:
            return self.sftool_id.getSFerror(pt,abs(eta))
        else:
            return 0.
    
    def getIsoSF(self, pt, eta):
        """Get SF for muon isolation."""
        return self.sftool_iso.getSF(pt,abs(eta))
        

    def getIdSFerror(self, pt, eta):
        """Get SF for muon isolation."""
        return self.sftool_iso.getSFerror(pt,abs(eta))
        
