# Author: Izaak Neutelings (May 2018)
# Adapted from
#   nanoAOD-tools/python/postprocessing/modules/jme/jetSmearer.py
#   https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/jme/jetSmearer.py
# Sources:
#   https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
#   https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyResolution
#   https://github.com/cms-jet/JRDatabase/tree/master/textFiles/
#   https://github.com/cms-nanoAOD/cmssw/blob/master-cmsswmaster/PhysicsTools/PatUtils/interface/SmearedJetProducerT.h
from tools import modulepath, ensureFile
import os, tarfile, tempfile
import numpy as np
from math import sqrt
from ROOT import gSystem, TRandom3, PyJetParametersWrapper, PyJetResolutionWrapper, PyJetResolutionScaleFactorWrapper
pathJME = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoAODTools/data/jme/"
pathJME_local = modulepath+"/jetMET/"



class JetSmearer:
    """Class to smear jet pT to account for measured difference in jet energy resolution (JER)
    between data and simulation."""
    
    def __init__(self, globalTag=None, jetType="AK4PFchs", jmr_vals=[1.09, 1.14, 1.04], year=2017, systematics=True):
        
        #--------------------------------------------------------------------------------------------
        # CV: globalTag and jetType not yet used, as there is no consistent set of txt files for
        #     JES uncertainties and JER scale factors and uncertainties yet
        #--------------------------------------------------------------------------------------------
        
        # GLOBAL TAG
        if globalTag==None:
          if year==2016:
            globalTag = "Summer16_25nsV1_MC" #Fall17_25nsV1_MC
          elif year==2017:
            globalTag = "Fall17_V3_MC"
          elif year==2018:
            globalTag = "Autumn18_V1_MC"
        
        # READ JER and JER scale factors and uncertainties
        # from https://github.com/cms-jet/JRDatabase/tree/master/textFiles/ )
        from JetMETCorrectionTool import ensureJMEFiles
        path_JER    = ensureJMEFiles(globalTag,JER=True)
        filename    = ensureFile(path_JER,"%s_PtResolution_%s.txt"%(globalTag,jetType))
        filenameUnc = ensureFile(path_JER,"%s_SF_%s.txt"%(globalTag,jetType))
        
        # LOAD LIBRARIES for accessing JER scale factors and uncertainties from txt files
        for library in [ "libCondFormatsJetMETObjects", "libPhysicsToolsNanoAODTools" ]:
          if library not in gSystem.GetLibraries():
            print("Load Library '%s'"%library.replace("lib", ""))
            gSystem.Load(library)
        
        # INITIALIZE JER scale factors and uncertainties (cf. PhysicsTools/PatUtils/interface/SmearedJetProducerT.h )
        print("Loading JER from file '%s'..."%filename)
        jer = PyJetResolutionWrapper(filename)
        print("Loading JER SFs and uncertainties from file '%s'..."%filenameUnc)
        jerSF_and_Uncertainty = PyJetResolutionScaleFactorWrapper(filenameUnc)
        
        self.path_JER                  = path_JER
        self.filename                  = filename
        self.filenameUnc               = filenameUnc
        self.params_sf_and_uncertainty = PyJetParametersWrapper()
        self.params_resolution         = PyJetParametersWrapper()
        self.jer                       = jer
        self.jerSF_and_Uncertainty     = jerSF_and_Uncertainty
        self.jmr_vals                  = jmr_vals
        self.enums_shift               = [0, 2, 1] if systematics else [0] # nom, up, down
        self.random                    = TRandom3(12345) # (needed for jet pT smearing)
        
    
    def endJob(self):
        ###"""Clean the temporary directories after the job is finished."""
        ###if '/tmp/' in self.path_JER:
        ###  print('JetSmearer.endJob: Removing "%s"...'%self.path_JER)
        ###  os.rmdir(self.path_JER)
        pass
        
    
    def smearJetPt(self, jet, genJet, rho):
        jet_pt_nom, jet_pt_jerUp, jet_pt_jerDown = self.smearPt(jet,genJet,rho)
        return ( jet_pt_nom*jet.pt, jet_pt_jerUp*jet.pt, jet_pt_jerDown*jet.pt )
        
    
    def smearPt(self, jetIn, genJetIn, rho):
        
        if hasattr(jetIn,'p4'):
          jet = jetIn.p4()
        else:
          jet = jetIn
        if hasattr(genJetIn,'p4'):
          genJet = genJetIn.p4()
        else:
          genJet = genJetIn
        
        #--------------------------------------------------------------------------------------------
        # CV: Smear jet pT to account for measured difference in JER between data and simulation.
        #     The function computes the nominal smeared jet pT simultaneously with the JER up and down shifts,
        #     in order to use the same random number to smear all three (for consistency reasons).
        #
        #     The implementation of this function follows PhysicsTools/PatUtils/interface/SmearedJetProducerT.h
        #--------------------------------------------------------------------------------------------
        
        if not (jet.Perp() > 0.):
            print("WARNING: jet pT = %1.1f !!"%jet.Perp())
            return ( 1., 1., 1. )
        
        SF_jet_pt = { }
        for enum_shift in self.enums_shift:
            self.params_sf_and_uncertainty.setJetEta(jet.Eta())
            SF_jet_pt[enum_shift] = self.jerSF_and_Uncertainty.getScaleFactor(self.params_sf_and_uncertainty, enum_shift)
        
        smear_vals = [ ]
        
        if genJet:
          for shift in self.enums_shift:
              
              # CASE 1: we have a "good" generator level jet matched to the reconstructed jet
              dPt = jet.Perp() - genJet.Perp()
              smearFactor = 1. + (SF_jet_pt[shift] - 1.)*dPt/jet.Perp()
              
              # check that smeared jet energy remains positive,
              if (smearFactor*jet.Perp()) < 1.e-2:
                  smearFactor = 1.e-2
              smear_vals.append(smearFactor)
              
        else:
          self.params_resolution.setJetPt(jet.Perp())
          self.params_resolution.setJetEta(jet.Eta())
          self.params_resolution.setRho(rho)
          jet_pt_resolution = self.jer.getResolution(self.params_resolution)
          rand = self.random.Gaus(0,jet_pt_resolution)
          for shift in self.enums_shift:
              
              # CASE 2: we don't have a generator level jet. Smear jet pT using a random Gaussian variation
              if SF_jet_pt[shift] > 1.:
                  smearFactor = 1. + rand * sqrt(SF_jet_pt[shift]**2 - 1.)
                  ###print smearFactor
              
              # CASE 3: we cannot smear this jet, as we don't have a generator level jet and the resolution in data is better
              #         than the resolution in the simulation, so we would need to randomly "unsmear" the jet, which is impossible
              else:
                  smearFactor = 1.
              
              # check that smeared jet energy remains positive,
              if (smearFactor*jet.Perp()) < 1.e-2:
                  smearFactor = 1.e-2
              smear_vals.append(smearFactor)
        
        ###print "%8.4f %8.4f %8.4f %s"%(jet.Pt(),jet_pt_resolution,smear_vals[0],genJet)
        return smear_vals
        
    
    
    def smearMass(self, jetIn, genJetIn):
        
        if hasattr(jetIn,'p4'):
            jet = jetIn.p4()
        else:
            jet = jetIn
        if hasattr(genJetIn,'p4'):
            genJet = genJetIn.p4()
        else:
            genJet = genJetIn
        
        #--------------------------------------------------------------------------------------------
        # CV: Smear jet mass to account for measured difference in JER between data and simulation.
        #     The function computes the nominal smeared jet mass simultaneously with the JER up and down shifts,
        #     in order to use the same random number to smear all three (for consistency reasons).
        #
        #     The implementation of this function follows PhysicsTools/PatUtils/interface/SmearedJetProducerT.h
        #--------------------------------------------------------------------------------------------
        
        if not (jet.M() > 0.):
            print("WARNING: jet m = %1.1f !!"%jet.M())
            return ( jet.M(), jet.M(), jet.M() )
        
        SF_jet_mass = dict(zip(self.enums_shift,self.jmr_vals))
        
        #### generate random number with flat distribution between 0 and 1
        ###u = self.random.Rndm()
        
        smear_vals = [ ]
        if genJet:
          for shift in self.enums_shift:
            
            # CASE 1: we have a "good" generator level jet matched to the reconstructed jet
            if genJetIn != None and genJet:
                dM = jet.M() - genJet.M()
                smearFactor = 1. + (SF_jet_mass[shift] - 1.)*dM/jet.M()
            
            # check that smeared jet energy remains positive
            if (smearFactor*jet.M()) < 1.e-2:
              smearFactor = 1.e-2
            smear_vals.append(smearFactor)
            
        else:        
          self.params_resolution.setJetPt(jet.Perp())
          self.params_resolution.setJetEta(jet.Eta())
          self.params_resolution.setRho(rho)
          jet_m_resolution = self.jer.getResolution(self.params_resolution)
          rand = self.random.Gaus(0,jet_m_resolution)
          for shift in self.enums_shift:
            
            # CASE 2: we don't have a generator level jet. Smear jet m using a random Gaussian variation
            if SF_jet_mass[shift] > 1.:
                smearFactor = 1. + rand * sqrt(SF_jet_mass[shift]**2 - 1.)
            
            # CASE 3: we cannot smear this jet, as we don't have a generator level jet and the resolution in data is better
            #        than the resolution in the simulation, so we would need to randomly "unsmear" the jet, which is impossible
            else:
                smearFactor = 1.
            
            # check that smeared jet energy remains positive
            if (smearFactor*jet.M()) < 1.e-2:
              smearFactor = 1.e-2
            smear_vals.append(smearFactor)
            
        return smear_vals
