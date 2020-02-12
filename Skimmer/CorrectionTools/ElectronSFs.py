from ROOT import TFile
import numpy as np
from ScaleFactorTool import ScaleFactor, ScaleFactorCalc
# https://twiki.cern.ch/twiki/bin/view/CMS/Egamma2017DataRecommendations#Efficiency_Scale_Factors
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgHLTScaleFactorMeasurements
#https://jskim.web.cern.ch/jskim/Public/HNWR_13TeV/EGammaTnP/
from global_paths import MAINDIR
path    = MAINDIR + 'CorrectionTools/leptonEfficiencies/ElectronPOG/'


class ElectronSFs:
    
    def __init__(self, year=2017):
        """Load histograms from files."""
        
        assert year in [2016,2017,2018], "ElectronSFs: You must choose a year from: 2016, 2017 or 2018."
        self.year = year
        if year==2016:
            self.sftool_trig_barrel    = ScaleFactor(path+"Run2016/Ele115orEleIso27orPho175_SF_2016.root",'SF_TH2F_Barrel','ele_trig_barrel')
            self.sftool_trig_endcap    = ScaleFactor(path+"Run2016/Ele115orEleIso27orPho175_SF_2016.root",'SF_TH2F_EndCap','ele_trig_endcap')
            self.sftool_reco  = ScaleFactor(path+"Run2016/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root","EGamma_SF2D",'ele_reco')
            self.sftool_idiso = ScaleFactor(path+"Run2016/2016LegacyReReco_ElectronLoose_Fall17V2.root","EGamma_SF2D",'ele_idiso') 
        elif year==2017:
            self.sftool_trig_barrel    = ScaleFactor(path+"Run2017/Ele115orEleIso35orPho200_SF_2017.root",'SF_TH2F_Barrel','ele_trig_barrel')
            self.sftool_trig_endcap    = ScaleFactor(path+"Run2017/Ele115orEleIso35orPho200_SF_2017.root",'SF_TH2F_EndCap','ele_trig_endcap')
            self.sftool_reco  = ScaleFactor(path+"Run2017/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root","EGamma_SF2D",'ele_reco')
            self.sftool_idiso = ScaleFactor(path+"Run2017/2017_ElectronLoose.root","EGamma_SF2D",'ele_idiso')
        elif year==2018: 
            self.sftool_trig_barrel    = ScaleFactor(path+"Run2018/Ele115orEleIso32orPho200_SF_2018.root",'SF_TH2F_Barrel','ele_trig_barrel')
            self.sftool_trig_endcap    = ScaleFactor(path+"Run2018/Ele115orEleIso32orPho200_SF_2018.root",'SF_TH2F_EndCap','ele_trig_endcap')
            self.sftool_reco  = ScaleFactor(path+"Run2018/egammaEffi.txt_EGM2D_updatedAll.root","EGamma_SF2D",'ele_reco')
            self.sftool_idiso = ScaleFactor(path+"Run2018/2018_ElectronLoose.root","EGamma_SF2D",'ele_idiso')
        
    
    def getTriggerSF(self, pt, eta):
        """Get SF for single electron trigger."""
        if eta > 1.4 and eta < 1.5:
            eta = 1.4
        elif eta > 1.5 and eta < 1.6:
            eta = 1.6
        elif eta < -1.4 and eta > -1.5:
            eta = -1.4
        elif eta < -1.5 and eta > -1.6:
            eta = -1.6
        if abs(eta) > 1.5:
            sf_trigger = self.sftool_trig_endcap.getSF(pt,eta)
        else:
            sf_trigger = self.sftool_trig_barrel.getSF(pt,eta)
        return sf_trigger

    def getTriggerSFerror(self, pt, eta):
        """Get SF error for single electron trigger."""
        if eta > 1.4 and eta < 1.5:
            eta = 1.4
        elif eta > 1.5 and eta < 1.6:
            eta = 1.6
        elif eta < -1.4 and eta > -1.5:
            eta = -1.4
        elif eta < -1.5 and eta > -1.6:
            eta = -1.6
        if abs(eta)>1.5:
            sf_trigger_error = self.sftool_trig_endcap.getSFerror(pt,eta)
        else:
            sf_trigger_error = self.sftool_trig_barrel.getSFerror(pt,eta)
        return sf_trigger_error       


    def getIdIsoSF(self, pt, eta):
        """Get SF for electron identification + isolation."""
        sf_reco  = self.sftool_reco.getSF(pt,eta) if self.sftool_reco else 1.
        sf_idiso = self.sftool_idiso.getSF(pt,eta)
        return sf_reco * sf_idiso

    def getIdIsoSFerror(self, pt, eta):
        """Get SF error for electron identification + isolation."""
        sf_reco  = self.sftool_reco.getSF(pt,eta) if self.sftool_reco else 1.
        sf_idiso = self.sftool_idiso.getSF(pt,eta)
        sf_reco_error = self.sftool_reco.getSFerror(pt,eta)
        sf_idiso_error = self.sftool_idiso.getSFerror(pt,eta)
        sf_reco_idiso_error = np.sqrt((sf_reco_error*sf_idiso)**2+(sf_idiso_error*sf_reco)**2)
        return sf_reco_idiso_error
