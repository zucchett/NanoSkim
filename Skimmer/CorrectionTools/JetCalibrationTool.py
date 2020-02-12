# Author: Izaak Neutelings (May 2018)
# Inspired on
#   nanoAOD-tools/python/postprocessing/modules/jme/JetReCalibrator.py
#   https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/jme/JetReCalibrator.py
# Sources:
#   https://github.com/cms-jet/JECDatabase/raw/master/tarballs/
from tools import modulepath, ensureFile
import os, re
from ROOT import gSystem, vector, JetCorrectorParameters, JetCorrectionUncertainty, FactorizedJetCorrector
pathJEC = modulepath+"/JetMET/"


class JetReCalibrator:
    
    def __init__(self,globalTag,jetFlavour,doResidualJECs=True,**kwargs):
        """Create a corrector object that reads the payloads from the text dumps of a global tag under
        CMGTools/RootTools/data/jec  (see the getJec.py there to make the dumps).
        It will apply the L1,L2,L3 and possibly the residual corrections to the jets.
        If configured to do so, it will also compute the type1 MET corrections."""
        
        globalTag        = globalTag
        jetFlavour       = jetFlavour
        doResidualJECs   = doResidualJECs
        era              = kwargs.get('era',             ""      )
        path             = kwargs.get('path',            pathJEC )
        upToLevel        = kwargs.get('upToLevel',       3       )
        correctType1MET  = kwargs.get('correctType1MET', False   )
        correctSeparate  = kwargs.get('correctSeparate', False   )
        type1METParams   = kwargs.get('type1METParams',  {'jetPtThreshold':15., 'skipEMfractionThreshold':0.9, 'skipMuons':True})
        ###if era:
        ###  globalTag = re.sub(r"(201[678])(_V\d+)",r"\1%s\2"%era,globalTag)
        
        # BASE CORRECTIONS
        path           = os.path.expandvars(path) #"%s/src/CMGTools/RootTools/data/jec"%os.environ['CMSSW_BASE'];
        print("Loading JES corrections from '%s' with globalTag '%s'..."%(path,globalTag))
        filenameL1     = ensureFile("%s/%s_L1FastJet_%s.txt"%( path,globalTag,jetFlavour))
        filenameL2     = ensureFile("%s/%s_L2Relative_%s.txt"%(path,globalTag,jetFlavour))
        filenameL3     = ensureFile("%s/%s_L3Absolute_%s.txt"%(path,globalTag,jetFlavour))
        self.L1JetPar  = JetCorrectorParameters(filenameL1,"");
        self.L2JetPar  = JetCorrectorParameters(filenameL2,"");
        self.L3JetPar  = JetCorrectorParameters(filenameL3,"");
        self.vPar      = vector(JetCorrectorParameters)()
        self.vPar.push_back(self.L1JetPar)
        if upToLevel>=2: self.vPar.push_back(self.L2JetPar)
        if upToLevel>=3: self.vPar.push_back(self.L3JetPar)
        
        # ADD RESIDUALS
        if doResidualJECs:
            filenameL2L3   = ensureFile("%s/%s_L2L3Residual_%s.txt"%(path,globalTag,jetFlavour))
            self.ResJetPar = JetCorrectorParameters(filenameL2L3)
            self.vPar.push_back(self.ResJetPar)
        
        # STEP 3: Construct a FactorizedJetCorrector object
        self.JetCorrector = FactorizedJetCorrector(self.vPar)
        if os.path.exists("%s/%s_Uncertainty_%s.txt"%(path,globalTag,jetFlavour)):
            self.JetUncertainty = JetCorrectionUncertainty("%s/%s_Uncertainty_%s.txt"%(path,globalTag,jetFlavour));
        elif os.path.exists("%s/Uncertainty_FAKE.txt"%path):
            self.JetUncertainty = JetCorrectionUncertainty("%s/Uncertainty_FAKE.txt"%path);
        else:
            print 'Missing JEC uncertainty file "%s/%s_Uncertainty_%s.txt", so jet energy uncertainties will not be available'%(path,globalTag,jetFlavour)
            self.JetUncertainty = None
        self.separateJetCorrectors = { }
        if correctSeparate or correctType1MET:
            self.vParL1 = vector(JetCorrectorParameters)()
            self.vParL1.push_back(self.L1JetPar)
            self.separateJetCorrectors['L1'] = FactorizedJetCorrector(self.vParL1)
            if upToLevel >= 2 and correctSeparate:
                self.vParL2 = vector(JetCorrectorParameters)()
                for i in [self.L1JetPar,self.L2JetPar]: self.vParL2.push_back(i)
                self.separateJetCorrectors['L1L2'] = FactorizedJetCorrector(self.vParL2)
            if upToLevel >= 3 and correctSeparate:
                self.vParL3 = vector(JetCorrectorParameters)()
                for i in [self.L1JetPar,self.L2JetPar,self.L3JetPar]: self.vParL3.push_back(i)
                self.separateJetCorrectors['L1L2L3'] = FactorizedJetCorrector(self.vParL3)
            if doResidualJECs and correctSeparate:
                self.vParL3Res = vector(JetCorrectorParameters)()
                for i in [self.L1JetPar,self.L2JetPar,self.L3JetPar,self.ResJetPar]: self.vParL3Res.push_back(i)
                self.separateJetCorrectors['L1L2L3Res'] = FactorizedJetCorrector(self.vParL3Res)
        
        self.globalTag        = globalTag
        self.jetFlavour       = jetFlavour
        self.doResidualJECs   = doResidualJECs
        self.path             = path
        self.upToLevel        = upToLevel
        self.correctType1MET  = correctType1MET
        self.correctSeparate  = correctSeparate
        self.type1METParams   = type1METParams
        
    
    
    def getCorrection(self,jet,rho,delta=0,corrector=None):
        """Compute correction for a given jet."""
        
        if not corrector:
          corrector = self.JetCorrector
        if corrector != self.JetCorrector and delta!=0:
          raise RuntimeError('Configuration not supported')
        
        corrector.setJetEta(jet.eta)
        corrector.setJetPt(jet.pt*(1.-jet.rawFactor))
        corrector.setJetA(jet.area)
        corrector.setRho(rho)
        corr = corrector.getCorrection()
        
        if delta != 0:
          if not self.JetUncertainty:
            raise RuntimeError("Jet energy scale uncertainty shifts requested, but not available")
          self.JetUncertainty.setJetEta(jet.eta)
          self.JetUncertainty.setJetPt(corr * jet.pt * (1.-jet.rawFactor))
          try:
              jet.jetEnergyCorrUncertainty = self.JetUncertainty.getUncertainty(True) 
          except RuntimeError as r:
              print "Caught %s when getting uncertainty for jet of pt %.1f, eta %.2f\n"%(r,corr * jet.pt * (1.-jet.rawFactor),jet.eta)
              jet.jetEnergyCorrUncertainty = 0.5
          #print "   jet with corr pt %6.2f has an uncertainty %.2f "%(jet.pt()*jet.rawFactor()*corr, jet.jetEnergyCorrUncertainty)
          corr *= max(0, 1+delta*jet.jetEnergyCorrUncertainty)
        
        #print "%10.4f %10.4f %10.5f %10.5f"%(jet.pt,jet.eta,jet.rawFactor,corr)
        return corr
        
    
    
    def correct(self,jet,rho,delta=0,addCorr=False,addShifts=False, metShift=[0,0]):
        """Corrects a jet energy (optionally shifting it also by delta times the JEC uncertainty)
           If addCorr, set jet.corr to the correction.
           If addShifts, set also the +1 and -1 jet shifts
           The metShift vector will accumulate the x and y changes to the MET from the JEC, i.e. the
           negative difference between the new and old jet momentum, for jets eligible for type1 MET
           corrections, and after subtracting muons. The pt cut is applied to the new corrected pt.
           This shift can be applied on top of the *OLD TYPE1 MET*, but only if there was no change
           in the L1 corrections nor in the definition of the type1 MET (e.g. jet pt cuts).
        """
        raw = 1.-jet.rawFactor
        corr = self.getCorrection(jet,rho,delta)
        ###print "%8.4f %8.4f %8.4f"%(jet.pt,raw,corr)
        if corr <= 0:
            return jet.pt
        newpt   = raw*corr*jet.pt
        newmass = raw*corr*jet.mass
        return newpt, newmass
