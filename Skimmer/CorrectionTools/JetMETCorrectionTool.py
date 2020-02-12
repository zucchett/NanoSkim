# Author: Izaak Neutelings (May 2018)
# Adapted from
#   nanoAOD-tools/python/postprocessing/modules/jme/jetmetUncertainties.py
#   https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/jme/jetmetUncertainties.py
#   https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/python/postprocessing/modules/jme/jetRecalib.py (data)
from tools import modulepath, ensureFile
from ROOT import gSystem, TLorentzVector, vector, JetCorrectorParameters, JetCorrectionUncertainty, FactorizedJetCorrector
import math, os, glob, tarfile, tempfile
import numpy as np
from math import sqrt, atan2, cos, sin
from JetCalibrationTool import JetReCalibrator
from JetSmearingTool import JetSmearer
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.tools import matchObjectCollection, matchObjectCollectionMultiple
pathJME = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoAODTools/data/jme/"
pathJME_local = modulepath+"/jetMET/"



def ensureJMEFiles(globalTag,path=None,tarbalpath=pathJME_local,JER=False):
    """Help function to ensure the JEC files are available in a given path. If not, look for a tar ball."""
    # https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
    # https://github.com/cms-jet/JECDatabase/raw/master/tarballs/
    # https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
    # https://github.com/cms-jet/JRDatabase/tree/master/textFiles/
    
    if path==None:
      path = os.path.join(tarbalpath,globalTag)
    
    # CHECK if txt files are already there
    if os.path.exists(path):
      if JER:
        files_sf_txt  = glob.glob(os.path.join(path,globalTag+"*_SF_*.txt"))
        files_res_txt = glob.glob(os.path.join(path,globalTag+"*Resolution_*.txt"))
        if len(files_sf_txt)>=1 and len(files_res_txt)>=3:
          return path
      else:
        files_jes_txt = glob.glob(os.path.join(path,"*_L[123]*.txt"))
        files_unc_txt = glob.glob(os.path.join(path,"*_Uncertainty*.txt"))
        if len(files_jes_txt)>=6 and len(files_unc_txt)>=2:
          return path
    else:
      os.makedirs(path)
    
    # CHECK for tarball and extract to directory
    tarbalpath = pathJME_local
    for ext in [".tar.gz",".tgz"]:
      files_tgz = glob.glob(os.path.join(tarbalpath+globalTag+ext))
      if len(files_tgz)>0:
        tarfilename = files_tgz[0]
        print("Extracting %s to %s..."%(tarfilename,path))
        archive = tarfile.open(tarfilename, "r:gz")
        archive.extractall(path)
        return path
    
    #path_JEC   = tempfile.mkdtemp()
    #jesArchive = tarfile.open(pathJME+globalTag+".tgz", "r:gz")
    #jesArchive.extractall(path_JEC)
    #return path_JEC
    
    url = "https://github.com/cms-jet/JRDatabase/tree/master/textFiles/" if JER else "https://github.com/cms-jet/JECDatabase/raw/master/tarballs/"
    raise OSError("ensureJECFiles: did not find txt files or tarball for global tag in '%s'! Check %s"%(globalTag,url))
    return None
    


class JetMETCorrectionTool:
    """Class to apply jet/MET corrections on an event-by-event basis."""
    
    def __init__(self, year, **kwargs):
        
        #--------------------------------------------------------------------------------------------
        # CV: globalTag and jetType not yet used, as there is no consistent set of txt files for
        #     JES uncertainties and JER scale factors and uncertainties yet
        #--------------------------------------------------------------------------------------------
        
        globalTag        = kwargs.get('globalTag',        None       )
        globalTag_JER    = kwargs.get('globalTag_JER',    None       )
        globalTag_JES    = kwargs.get('globalTag_JES',    globalTag  )
        jetType          = kwargs.get('jet',              'AK4PFchs' )
        metType          = kwargs.get('met',              'MET'      )
        isData           = kwargs.get('data',             False      )
        era              = kwargs.get('era',              ""         ) # for data; A, B, C, D, ...
        redoJEC          = kwargs.get('redoJEC',          True       )
        doJER            = kwargs.get('smear',            not isData ) and not isData
        doSystematics    = kwargs.get('systematics',      True       ) and not isData
        noGroom          = kwargs.get('noGroom',          True       )
        jesUncertainties = kwargs.get('uncertainties',    ['Total'] if doSystematics else [ ] )
        updateEvent      = kwargs.get('updateEvent',      False      ) # unreliable...
        correctSeparate  = kwargs.get('correctSeparate',  False      )
        
        jetTypes = ['AK4PFchs','AK4PFPuppi','AK8PFchs','AK8PFPuppi']
        assert year in [2016,2017,2018], "JetMETCorrectionTool: You must choose a year from: 2016, 2017, or 2018."
        assert jetType in jetTypes, "JetMETCorrectionTool: You must choose a jet type from: %s"%(', '.join(jetTypes))
        assert all(u in ['Total','All'] for u in jesUncertainties), "JetMETCorrectionTool: Given uncertainties are %s; must be 'Total' or 'All'!"%(jesUncertainties)
        
        # TARGET VARIABLES
        if "AK4" in jetType:
            self.jetBranchName       = 'Jet'
            self.genJetBranchName    = 'GenJet'
            self.genSubJetBranchName = None
            self.doGroomed           = False
            self.corrMET             = True
        elif "AK8" in jetType:
            self.jetBranchName       = 'FatJet'
            self.subJetBranchName    = 'SubJet'
            self.genJetBranchName    = 'GenJetAK8'
            self.genSubJetBranchName = 'SubGenJetAK8'
            self.doGroomed           = not noGroom
            self.corrMET             = False
        else:
            raise ValueError("ERROR: Invalid jet type = '%s'!"%jetType)
        self.metBranchName           = metType
        self.rhoBranchName           = "fixedGridRhoFastjetAll"
        self.jmsVals                 = [1.00, 0.99, 1.01] # TODO: change to real values
        self.unclEnThreshold         = 15. # energy threshold below which jets are considered as "unclustered energy"
                                           # cf. JetMETCorrections/Type1MET/python/correctionTermsPfMetType1Type2_cff.py
        jetSmearer                   = None
        jmr_vals                     = [ ]
        
        if isData:
          
          # GLOBAL TAG for JES
          if globalTag==None:
            if year==2016:
              for eraset in ['BCD','EF','GH']:
                if era in eraset: era = eraset
              globalTag     = "Summer16_07Aug2017_V11_DATA"
              globalTag_JES = "Summer16_07Aug2017%s_V11_DATA"%era
            elif year==2017:
              if era in 'DE': era = 'DE'
              globalTag     = "Fall17_17Nov2017_V32_DATA"
              globalTag_JES = "Fall17_17Nov2017%s_V32_DATA"%era
            else:
              era           = "Run"+era
              globalTag     = "Autumn18_V8_DATA"
              globalTag_JES = "Autumn18_%s_V8_DATA"%era
          
        else:
          
          # GLOBAL TAG for JES
          if globalTag==None:
            if year==2016:
              globalTag = "Summer16_07Aug2017_V11_MC" #"Summer16_23Sep2016V4_MC"
            elif year==2017:
              globalTag = "Fall17_17Nov2017_V32_MC"
            else:
              globalTag = "Autumn18_V8_MC"
            globalTag_JES = globalTag
          
          # GLOBAL TAG for JER
          if globalTag_JER==None:
            if year==2016:
              globalTag_JER = "Summer16_25nsV1_MC"
            elif year==2017:
              globalTag_JER = "Fall17_V3_MC"
            elif year==2018:
              globalTag_JER = "Autumn18_V1_MC"
          
          # JERs: https://twiki.cern.ch/twiki/bin/view/CMS/JetWtagging
          if year==2016 or year==2018: #update when 2018 values available
            jmr_vals = [1.00, 1.20, 0.80] # nominal, up, down
          else:
            jmr_vals = [1.09, 1.14, 1.04]
          
          # READ JER uncertainties
          ###if doJER:
          jetSmearer = JetSmearer(globalTag_JER,jetType,systematics=doSystematics,jmr_vals=jmr_vals)
        
        # READ JES
        path_JES = ensureJMEFiles(globalTag)
        
        # REDO JECs
        if redoJEC:
          jetReCalibrator = JetReCalibrator(globalTag_JES,jetType,True,path=path_JES,
                                            correctSeparate=correctSeparate,correctType1MET=False)
        else:
          jetReCalibrator = None
        
        # LOAD LIBRARIES for accessing JES scale factors and uncertainties from txt files
        for library in [ "libCondFormatsJetMETObjects", "libPhysicsToolsNanoAODTools" ]:
          if library not in gSystem.GetLibraries():
            print("Load Library '%s'"%library.replace("lib", ""))
            gSystem.Load(library)
        
        # READ UNCERTAINTY SOURCE NAMES from the loaded file
        jesUncertainty = { }
        filename_JES   = ""
        if doSystematics:
          postfix = '' if jesUncertainties==['Total'] else "Sources"
          filename_JES = ensureFile(path_JES,"%s_Uncertainty%s_%s.txt"%(globalTag,postfix,jetType))
          if jesUncertainties==['All']:
            with open(path_JES+'/'+filename_JES) as file:
              lines   = file.read().split("\n")
              sources = filter(lambda x: x.startswith("[") and x.endswith("]"), lines)
              sources = map(lambda x: x[1:-1], sources)
              jesUncertainties = sources
          
          # CREATE JES uncertainties
          print("Loading JES uncertainties from file '%s'..."%filename_JES)
          #jesUncertainty = JetCorrectionUncertainty(filename_JES)
          # implementation didn't seem to work for factorized JEC, try again another way
          for uncertainty in jesUncertainties:
            unclabel = '' if uncertainty=='Total' and len(jesUncertainties)==1 else uncertainty
            pars = JetCorrectorParameters(filename_JES,unclabel)
            jesUncertainty[uncertainty] = JetCorrectionUncertainty(pars)
        
        self.year             = year
        self.globalTag        = globalTag
        self.jetType          = jetType
        self.metType          = metType
        self.isData           = isData
        self.era              = era
        self.redoJEC          = redoJEC
        ###self.doJER            = doJER
        self.doSystematics    = doSystematics
        self.noGroom          = noGroom
        self.updateEvent      = updateEvent
        self.jesUncertainties = jesUncertainties  # list
        self.jesUncertainty   = jesUncertainty    # dictionairy
        self.path_JES         = path_JES
        self.filename_JES     = filename_JES
        self.jmr_vals         = jmr_vals
        self.jetSmearer       = jetSmearer
        self.jetReCalibrator  = jetReCalibrator
        self.correctJetMET    = self.correctJetMET_Data if isData else self.correctJetMET_MC
        
    
    def endJob(self):
        ###"""Clean the temporary directories after the job is finished."""
        ###if '/tmp/' in self.path_JES[:5]:
        ###  print('JetSmearer.endJob: Removing "%s"...'%self.path_JES)
        ###  os.rmdir(self.path_JES)
        ###self.jetSmearer.endJob()
        pass
        
    
    def correctJetMET_Data(self, event):
        """Process data event."""
        ###print ">>> %8s "%event.event + '-'*80
        
        # NOMINAL VALUES
        jets_pt_nom = [ ]
        if self.corrMET:
            met = Object(event, self.metBranchName)
            met_px_nom, met_py_nom = met.pt*cos(met.phi), met.pt*sin(met.phi)
        
        # APPLY JEC per jet
        jets = Collection(event, self.jetBranchName )
        rho  = getattr(event, self.rhoBranchName)
        for jet in jets:
            
            # RAW VALUES
            jet_pt0   = jet.pt
            if hasattr(jet,'rawFactor'):
              jet_pt_raw = jet_pt0 * (1 - jet.rawFactor)
            else:
              jet_pt_raw = -1.0 * jet_pt0 # if factor not present factor will be saved as -1
            
            # CALIBRATE - apply JES corrections
            if self.redoJEC:
              jet_pt_nom, jet_mass_nom = self.jetReCalibrator.correct(jet,rho)
              jet.pt   = jet_pt_nom
              jet.mass = jet_mass_nom
            else:
              jet_pt_nom   = jet.pt
              jet_mass_nom = jet.mass
            jets_pt_nom.append(jet_pt_nom)
            ###print "%10.4f %10.4f %10.5f %10.5f"%(jet_pt_raw,jet_pt_nom,jet.eta,jet.rawFactor)
            ###print "%10.4f %8.4f %8.4f %10.6f %10.6f"%(jet_pt_raw, jet_pt0, jet_pt_nom, jet.rawFactor, jet_pt_nom/jet_pt_raw-1.)
            
            #### UPDATE JET in event
            ###if self.updateEvent:
            ###  getattr(event,self.jetBranchName+'_pt')[jet._index] = jet_pt_nom
            
            # PROPAGATE JES corrections to MET
            if self.corrMET and jet_pt_nom > self.unclEnThreshold:
              jet_cosPhi = cos(jet.phi)
              jet_sinPhi = sin(jet.phi)
              met_px_nom = met_px_nom - (jet_pt_nom - jet_pt0)*jet_cosPhi
              met_py_nom = met_py_nom - (jet_pt_nom - jet_pt0)*jet_sinPhi
        
        # PREPARE MET for return
        if self.corrMET:
            met_nom = TLorentzVector(met_px_nom,met_py_nom,0,sqrt(met_px_nom**2+met_py_nom**2))
            ###if self.updateEvent:
            ###  setattr(event,self.metBranchName+'_pt',  met_vars['nom'].Pt())
            ###  setattr(event,self.metBranchName+'_phi', met_vars['nom'].Phi())
            return jets_pt_nom, met_nom
        
        return jets_pt_nom
        
    
    
    def correctJetMET_MC(self, event):
        """Process event, apply corrections."""
        ###print ">>> %8s "%event.event + '-'*80
        
        ###if self.doGroomed:
        ###    subJets = Collection(event, self.subJetBranchName )
        ###    genSubJets = Collection(event, self.genSubJetBranchName )
        ###    genSubJetMatcher = matchObjectCollectionMultiple( genJets, genSubJets, dRmax=0.8 )
        
        jets_pt_nom       = [ ]
        ###jets_mass_nom     = [ ]
        if self.doSystematics:
            jets_pt_jerUp     = [ ]
            jets_pt_jerDown   = [ ]
            jets_pt_jesUp     = { }
            jets_pt_jesDown   = { }
            ###jets_mass_jerUp   = [ ]
            ###jets_mass_jerDown = [ ]
            ###jets_mass_jmrUp   = [ ]
            ###jets_mass_jmrDown = [ ]
            ###jets_mass_jesUp   = { }
            ###jets_mass_jesDown = { }
            ###jets_mass_jmsUp   = [ ]
            ###jets_mass_jmsDown = [ ]
            for uncertainty in self.jesUncertainties:
                jets_pt_jesUp[uncertainty]     = [ ]
                jets_pt_jesDown[uncertainty]   = [ ]
                ###jets_mass_jesUp[uncertainty]   = [ ]
                ###jets_mass_jesDown[uncertainty] = [ ]
        
        if self.corrMET:
            met = Object(event, self.metBranchName)
            met_px,         met_py         = met.pt*cos(met.phi), met.pt*sin(met.phi)
            met_px_nom,     met_py_nom     = met_px, met_py
            met_px_jerUp,   met_py_jerUp   = met_px, met_py
            met_px_jerDown, met_py_jerDown = met_px, met_py
            met_px_jesUp,   met_py_jesUp   = { }, { }
            met_px_jesDown, met_py_jesDown = { }, { }
            for uncertainty in self.jesUncertainties:
                met_px_jesUp[uncertainty]   = met_px
                met_py_jesUp[uncertainty]   = met_py
                met_px_jesDown[uncertainty] = met_px
                met_py_jesDown[uncertainty] = met_py
        
        ###if self.doGroomed:
        ###    jets_msdcorr_nom = [ ]
        ###    if self.doSystematics:
        ###        jets_msdcorr_jerUp   = [ ]
        ###        jets_msdcorr_jerDown = [ ]
        ###        jets_msdcorr_jmrUp   = [ ]
        ###        jets_msdcorr_jmrDown = [ ]
        ###        jets_msdcorr_jesUp   = { }
        ###        jets_msdcorr_jesDown = { }
        ###        jets_msdcorr_jmsUp   = [ ]
        ###        jets_msdcorr_jmsDown = [ ]
        ###        for uncertainty in self.jesUncertainties:
        ###            jets_msdcorr_jesUp[uncertainty]   = [ ]
        ###            jets_msdcorr_jesDown[uncertainty] = [ ]
        
        # MATCH reconstructed jets to generator level ones
        # (needed to evaluate JER scale factors and uncertainties)
        jets    = Collection(event, self.jetBranchName)
        genJets = Collection(event, self.genJetBranchName)
        rho     = getattr(event, self.rhoBranchName)
        pairs   = matchObjectCollection(jets, genJets)
        # APPLY JEC per jet
        for jet in jets:
            genJet = pairs[jet]
            
            ###if self.doGroomed:
            ###    genGroomedSubJets = genSubJetMatcher[genJet] if genJet!=None else None
            ###    genGroomedJet = genGroomedSubJets[0].p4() + genGroomedSubJets[1].p4() if genGroomedSubJets!=None and len(genGroomedSubJets)>=2 else None
            ###    if jet.subJetIdx1>=0 and jet.subJetIdx2>=0:
            ###        groomedP4 = subJets[ jet.subJetIdx1 ].p4() + subJets[ jet.subJetIdx2].p4()
            ###    else:
            ###        groomedP4 = None
            
            # RAW VALUES
            jet_pt0   = jet.pt
            ###jet_mass0 = jet.mass
            if hasattr(jet,'rawFactor'):
              jet_pt_raw = jet_pt0 * (1 - jet.rawFactor)
              ###jet_mass_raw = jet.mass * (1 - jet.rawFactor)
            else:
              jet_pt_raw = -1.0 * jet_pt0 # if factor not present factor will be saved as -1
              ###jet_mass_raw = -1.0 * jet.mass
            
            # CALIBRATE - apply JES corrections
            if self.redoJEC:
              jet_pt, jet_mass = self.jetReCalibrator.correct(jet,rho)
              jet.pt   = jet_pt
              jet.mass = jet_mass
            else:
              jet_pt   = jet.pt
              jet_mass = jet.mass
            
            # SMEAR - apply JER SF
            if self.doSystematics:
              smear_jer, smear_jerUp, smear_jerDown = self.jetSmearer.smearPt(jet,genJet,rho)
            else:
              smear_jer = self.jetSmearer.smearPt(jet,genJet,rho)[0]
            jet_pt_nom  = smear_jer*jet_pt
            if jet_pt_nom<0.0:
              jet_pt_nom *= -1.0
            jets_pt_nom.append(jet_pt_nom)
            ###print "%8.4f %8.4f %8.4f %8.4f %8.4f %8.4f"%(jet_pt_raw, jet_pt0, jet_pt, jet_pt_nom, jet.rawFactor, smear_jer)
            
            #### SMEAR JMS and JMR scale factors
            ###jmsNomVal  = self.jmsVals[0]
            ###jmsDownVal = self.jmsVals[1]
            ###jmsUpVal   = self.jmsVals[2]
            ###smear_jmr, smear_jmrUp, smear_jmrDown = self.jetSmearer.smearMass(jet, genJet)
            ###jet_mass_nom           = smear_jer*smear_jmr*jmsNomVal*jet.mass
            ###if jet_mass_nom < 0.0:
            ###    jet_mass_nom *= -1.0
            ###jets_mass_nom    .append(jet_mass_nom)
            
            #### CORRECT GROOMED JETS
            ###if self.doGroomed:
            ###    ( jet_msdcorr_jmrNomVal, jet_msdcorr_jmrUpVal, jet_msdcorr_jmrDownVal ) = self.jetSmearer.getSmearValsM(groomedP4, genGroomedJet) if groomedP4!=None and genGroomedJet!=None else (0.,0.,0.)
            ###    jet_msdcorr_raw = groomedP4.M() if groomedP4!=None else 0.0
            ###    if jet_msdcorr_raw < 0.0:
            ###        jet_msdcorr_raw *= -1.0
            ###    jet_msdcorr_nom           = smear_jer*jet_msdcorr_jmrNomVal*jet_msdcorr_raw
            ###    jets_msdcorr_nom    .append(jet_msdcorr_nom)
            
            #### UPDATE JET in event (unreliable)
            ###if self.updateEvent:
            ###  getattr(event,self.jetBranchName+'_pt')[jet._index] = jet_pt_nom
            ###  ###getattr(event,self.jetBranchName+'_mass')[jet._index] = jet_mass_nom
            
            # EVALUATE JEC uncertainties
            if self.doSystematics:
                
                # EVALUATE JES uncertainties
                jet_pt_jesUp     = { }
                jet_pt_jesDown   = { }
                for uncertainty in self.jesUncertainties:
                    # (cf. https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JetCorUncertainties )
                    self.jesUncertainty[uncertainty].setJetPt(jet_pt_nom)
                    self.jesUncertainty[uncertainty].setJetEta(jet.eta)
                    delta = self.jesUncertainty[uncertainty].getUncertainty(True)
                    jet_pt_jesUp[uncertainty]   = jet_pt_nom*(1.+delta)
                    jet_pt_jesDown[uncertainty] = jet_pt_nom*(1.-delta)
                    jets_pt_jesUp[uncertainty]  .append(jet_pt_jesUp[uncertainty])
                    jets_pt_jesDown[uncertainty].append(jet_pt_jesDown[uncertainty])
                    ###jet_mass_jesUp   [uncertainty] = jet_mass_nom*(1. + delta)
                    ###jet_mass_jesDown [uncertainty] = jet_mass_nom*(1. - delta)
                    ###jets_mass_jesUp  [uncertainty].append(jet_mass_jesUp[uncertainty])
                    ###jets_mass_jesDown[uncertainty].append(jet_mass_jesDown[uncertainty])
                    ###if self.doGroomed:
                    ###    jet_msdcorr_jesUp   [uncertainty] = jet_msdcorr_nom*(1. + delta)
                    ###    jet_msdcorr_jesDown [uncertainty] = jet_msdcorr_nom*(1. - delta)
                    ###    jets_msdcorr_jesUp  [uncertainty].append(jet_msdcorr_jesUp[uncertainty])
                    ###    jets_msdcorr_jesDown[uncertainty].append(jet_msdcorr_jesDown[uncertainty])
                
                # EVALUATE JER uncertainties
                jet_pt_jerUp   = smear_jerUp*jet_pt
                jet_pt_jerDown = smear_jerDown*jet_pt
                jets_pt_jerUp  .append(jet_pt_jerUp)
                jets_pt_jerDown.append(jet_pt_jerDown)
                
                #### EVALUATE JMS and JMR uncertainties
                ###jet_mass_jesUp   = { }
                ###jet_mass_jesDown = { }
                ###jet_mass_jmsUp   = [ ]
                ###jet_mass_jmsDown = [ ]
                ###jets_mass_jerUp  .append(smear_jerUp  *smear_jmr *jmsNomVal *jet.mass)
                ###jets_mass_jerDown.append(smear_jerDown*smear_jmr *jmsNomVal *jet.mass)
                ###jets_mass_jmrUp  .append(smear_jer *smear_jmrUp  *jmsNomVal *jet.mass)
                ###jets_mass_jmrDown.append(smear_jer *smear_jmrDown*jmsNomVal *jet.mass)
                ###jets_mass_jmsUp  .append(smear_jer *smear_jmr    *jmsUpVal  *jet.mass)
                ###jets_mass_jmsDown.append(smear_jer *smear_jmr    *jmsDownVal*jet.mass)
                
                ###if self.doGroomed:
                ###    jet_msdcorr_jmsUp   = [ ]
                ###    jet_msdcorr_jmsDown = [ ]
                ###    jet_msdcorr_jesUp   = { }
                ###    jet_msdcorr_jesDown = { }
                ###    jets_msdcorr_jerUp  .append(smear_jerUp  *jet_msdcorr_jmrNomVal *jmsNomVal  *jet_msdcorr_raw)
                ###    jets_msdcorr_jerDown.append(smear_jerDown*jet_msdcorr_jmrNomVal *jmsNomVal  *jet_msdcorr_raw)
                ###    jets_msdcorr_jmrUp  .append(smear_jer *jet_msdcorr_jmrUpVal  *jmsNomVal  *jet_msdcorr_raw)
                ###    jets_msdcorr_jmrDown.append(smear_jer *jet_msdcorr_jmrDownVal*jmsNomVal  *jet_msdcorr_raw)
                ###    jets_msdcorr_jmsUp  .append(smear_jer *jet_msdcorr_jmrNomVal *jmsUpVal   *jet_msdcorr_raw)
                ###    jets_msdcorr_jmsDown.append(smear_jer *jet_msdcorr_jmrNomVal *jmsDownVal *jet_msdcorr_raw)
            
            # PROPAGATE JER and JES corrections and uncertainties to MET
            if self.corrMET and jet_pt_nom > self.unclEnThreshold:
                jet_cosPhi       = cos(jet.phi)
                jet_sinPhi       = sin(jet.phi)
                ###print "%8.4f - met_px_nom = met_px_nom - (jet_pt_nom - jet_pt0)*jet_cosPhi = %8.4f - (%8.4f - %8.4f)*%8.4f = %8.4f"%(jet.phi,met_px_nom,jet_pt_nom,jet_pt0,jet_cosPhi,met_px_nom-(jet_pt_nom-jet_pt0)*jet_cosPhi)
                met_px_nom       = met_px_nom     - (jet_pt_nom     - jet_pt0)*jet_cosPhi
                ###print "%8.4f - met_py_nom = met_py_nom - (jet_pt_nom - jet_pt0)*jet_sinPhi = %8.4f - (%8.4f - %8.4f)*%8.4f = %8.4f"%(jet.phi,met_py_nom,jet_pt_nom,jet_pt0,jet_sinPhi,met_py_nom-(jet_pt_nom-jet_pt0)*jet_sinPhi)
                met_py_nom       = met_py_nom     - (jet_pt_nom     - jet_pt0)*jet_sinPhi
                if self.doSystematics:
                  met_px_jerUp   = met_px_jerUp   - (jet_pt_jerUp   - jet_pt0)*jet_cosPhi
                  met_py_jerUp   = met_py_jerUp   - (jet_pt_jerUp   - jet_pt0)*jet_sinPhi
                  met_px_jerDown = met_px_jerDown - (jet_pt_jerDown - jet_pt0)*jet_cosPhi
                  met_py_jerDown = met_py_jerDown - (jet_pt_jerDown - jet_pt0)*jet_sinPhi
                  for uncertainty in self.jesUncertainties:
                      met_px_jesUp[uncertainty]   = met_px_jesUp[uncertainty]   - (jet_pt_jesUp[uncertainty]   - jet_pt0)*jet_cosPhi
                      met_py_jesUp[uncertainty]   = met_py_jesUp[uncertainty]   - (jet_pt_jesUp[uncertainty]   - jet_pt0)*jet_sinPhi
                      met_px_jesDown[uncertainty] = met_px_jesDown[uncertainty] - (jet_pt_jesDown[uncertainty] - jet_pt0)*jet_cosPhi
                      met_py_jesDown[uncertainty] = met_py_jesDown[uncertainty] - (jet_pt_jesDown[uncertainty] - jet_pt0)*jet_sinPhi
            
            #### CHECKS
            ###print ">>> %2d: jet.pt, jet_pt, corr_factor, smear_factor = %8.3f, %8.3f, %8.4f, %8.4f"%(jet._index,jet.pt,jet_pt,jet_pt/jet_pt_raw,smear_factor)
            ###print ">>> %2s  jet_pt_jerUp, jet_pt_nom, jet_pt_jerDown = %8.3f, %8.3f, %8.3f"%("",jet_pt_jerUp,jet_pt_nom,jet_pt_jerDown)
            ###print ">>> %2s  jet_pt_jesUp, jet_pt_nom, jet_pt_jesDown = %8.3f, %8.3f, %8.3f"%("",jet_pt_jesUp['Total'],jet_pt_nom,jet_pt_jesDown['Total'])
        
        # PREPARE JET PT variations for return; save 'Total' as just jesUp/jesDown
        if self.doSystematics:
          jetpt_vars = { 'nom': jets_pt_nom, 'jerUp': jets_pt_jerUp, 'jerDown': jets_pt_jerDown }
          for uncertainty in self.jesUncertainties:
              jetpt_vars["jes%sUp"%uncertainty.replace('Total','')]   = jets_pt_jesUp[uncertainty]
              jetpt_vars["jes%sDown"%uncertainty.replace('Total','')] = jets_pt_jesDown[uncertainty]
        else:
          jetpt_vars = { 'nom': jets_pt_nom, }
        
        if self.corrMET:
            
            # PREPARE MET for return
            ###print "met_px_nom = %8.4f"%(met_px_nom)
            ###print "met_py_nom = %8.4f"%(met_py_nom)
            met_vars = { 'nom': TLorentzVector(met_px_nom,met_py_nom,0,sqrt(met_px_nom**2+met_py_nom**2)) }
            
            #### UPDATE MET in event
            ###if self.updateEvent:
            ###  setattr(event,self.metBranchName+'_pt',  met_vars['nom'].Pt())
            ###  setattr(event,self.metBranchName+'_phi', met_vars['nom'].Phi())
            
            if self.doSystematics:
              
              # EVALUATE UNCLUSTERED ENERGY uncertainties
              met_deltaPx_unclEn = getattr(event,self.metBranchName+"_MetUnclustEnUpDeltaX")
              met_deltaPy_unclEn = getattr(event,self.metBranchName+"_MetUnclustEnUpDeltaY")
              met_px_unclEnUp    = met_px_nom + met_deltaPx_unclEn
              met_py_unclEnUp    = met_py_nom + met_deltaPy_unclEn
              met_px_unclEnDown  = met_px_nom - met_deltaPx_unclEn
              met_py_unclEnDown  = met_py_nom - met_deltaPy_unclEn
              
              # PREPARE MET variations for return
              met_vars['jesUp']      = { }
              met_vars['jesDown']    = { }
              met_vars['jerUp']      = TLorentzVector(met_px_jerUp,     met_py_jerUp,     0,sqrt(met_px_jerUp**2     +met_py_jerUp**2))
              met_vars['jerDown']    = TLorentzVector(met_px_jerDown,   met_py_jerDown,   0,sqrt(met_px_jerDown**2   +met_py_jerDown**2))
              met_vars['unclEnUp']   = TLorentzVector(met_px_unclEnUp,  met_py_unclEnUp,  0,sqrt(met_px_unclEnUp**2  +met_py_unclEnUp**2))
              met_vars['unclEnDown'] = TLorentzVector(met_px_unclEnDown,met_py_unclEnDown,0,sqrt(met_px_unclEnDown**2+met_py_unclEnDown**2))
              for uncertainty in self.jesUncertainties:
                  met_vars["jes%sUp"%uncertainty.replace('Total','')]   = TLorentzVector(met_px_jesUp[uncertainty],  met_py_jesUp[uncertainty],
                                                                                           0,sqrt(met_px_jesUp[uncertainty]**2  +met_py_jesUp[uncertainty]**2))
                  met_vars["jes%sDown"%uncertainty.replace('Total','')] = TLorentzVector(met_px_jesDown[uncertainty],met_py_jesDown[uncertainty],
                                                                                           0,sqrt(met_px_jesDown[uncertainty]**2+met_py_jesDown[uncertainty]**2))
            
            return jetpt_vars, met_vars
        
        return jetpt_vars
