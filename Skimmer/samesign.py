#!/usr/bin/env python
import os, sys, math
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import *

from CorrectionTools.PileupWeightTool import *
#from CorrectionTools.BTaggingTool import BTagWeightTool, BTagWPs
from CorrectionTools.MuonSFs import *
from CorrectionTools.ElectronSFs import *
from CorrectionTools.RecoilCorrectionTool import getTTptWeight, getTTPt
from CorrectionTools.DYCorrection import *
#from PileupWeightTool import PileupWeightTool
#from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeightProducer

from ROOT import TLorentzVector
from utils import EV, XS, getNameFromFile, recoverNeutrinoPz, getMinMuonJetDR

class SameSign(Module):
    def __init__(self):
        self.writeHistFile=True
        


    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
        self.event = 0
        self.hists = {}
        self.hists["Events"] = ROOT.TH1F("Events", "Events", 1, 0, 1)
#        self.addObject(self.h_events)
#        self.h_events.SetDirectory
    
    def endJob(self):
        Module.endJob(self)
        print "+ Module ended successfully,"#, self.h_events.GetEntries(), "events analyzed"
        pass
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("iSkim",  "I")
        self.out.branch("isMC",  "I")
        self.out.branch("isSingleMuIsoTrigger",  "I")
        self.out.branch("isSingleMuTrigger",  "I")
        self.out.branch("isDoubleMuonTrigger",  "I")
        self.out.branch("isSingleEleIsoTrigger",  "I")
        self.out.branch("isSingleEleTrigger",  "I")
        self.out.branch("passedMETFilters",  "I")
        self.out.branch("nCleanElectron",  "I")
        self.out.branch("nCleanMuon",  "I")
        self.out.branch("nCleanJet",  "I")
        self.out.branch("Z_mass",  "F")
        self.out.branch("Z_pt",  "F")
        self.out.branch("W_mass",  "F")
        self.out.branch("W_tmass",  "F")
        self.out.branch("W_pt",  "F")
        self.out.branch("ll_dEta",  "F")
        self.out.branch("ll_dPhi",  "F")
        self.out.branch("ll_dR",  "F")
        self.out.branch("Wqq_mass",  "F")
        self.out.branch("Tlvb1_mass",  "F")
        self.out.branch("Tlvb2_mass",  "F")
        self.out.branch("Tqqb1_mass",  "F")
        self.out.branch("Tqqb2_mass",  "F")
        self.out.branch("jj_mass",  "F")
        self.out.branch("jj_pt",  "F")
        self.out.branch("jj_dEta",  "F")
        self.out.branch("jj_dPhi",  "F")
        self.out.branch("jj_dR",  "F")
        self.out.branch("nj_mass",  "F")
        self.out.branch("vis_mass",  "F")
        self.out.branch("lljj_mass",  "F")
        self.out.branch("minMuonIso",  "F")
        self.out.branch("maxMuonIso",  "F")
        self.out.branch("minMuonMetDPhi",  "F")
        self.out.branch("maxMuonMetDPhi",  "F")
        self.out.branch("minMuonJetDR",  "F")
        self.out.branch("HT30",  "F")
        self.out.branch("nj20",  "I")
        self.out.branch("nj30",  "I")
        self.out.branch("nj40",  "I")
        self.out.branch("nBJet",  "I")
        self.out.branch("CSV1",  "F")
        self.out.branch("CSV2",  "F")
        self.out.branch("CSV3",  "F")
        self.out.branch("CSV4",  "F")
        self.out.branch("iCSV1",  "I")
        self.out.branch("iCSV2",  "I")
        self.out.branch("iCSV3",  "I")
        self.out.branch("iCSV4",  "I")
        self.out.branch("lumiWeight",  "F")
        self.out.branch("lheWeight",  "F")
        self.out.branch("stitchWeight",  "F")
        self.out.branch("puWeight",  "F")
        self.out.branch("topWeight",  "F")
        self.out.branch("qcdnloWeight",  "F")
        self.out.branch("qcdnnloWeight",  "F")
        self.out.branch("ewknloWeight",  "F")
        self.out.branch("triggerWeight",  "F")
        self.out.branch("leptonWeight",  "F")
        self.out.branch("eventWeightLumi",  "F")
        
        
        self.fileName = inputFile.GetName()
        self.sampleName = getNameFromFile(self.fileName)
        
        self.isMC = not "Run201" in self.fileName
        
        print "+ Opening file", self.fileName
        
        # b-tagging working points for DeepCSV
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
        if "Run2016" in self.fileName or "Summer16" in self.fileName:
            self.year = 2016
            self.lumi = 35920.
            self.btagLoose = 0.2217 #0.0614
            self.btagMedium = 0.6321 #0.3093
            self.btagTight = 0.8953 #0.7221
        elif "Run2017" in self.fileName or "Fall17" in self.fileName:
            self.year = 2017
            self.lumi = 41530.
            self.btagLoose = 0.1522 #0.0521
            self.btagMedium = 0.4941 #0.3033
            self.btagTight = 0.8001 #0.7489
        elif "Run2018" in self.fileName or "Autumn18" in self.fileName:
            self.year = 2018
            self.lumi = 59740.
            self.btagLoose = 0.1241 #0.0494
            self.btagMedium = 0.4184 #0.2770
            self.btagTight = 0.7527 #0.7264
        else:
            print "- Unknown year, aborting module"
            import sys
            sys.exit()
        
        self.xs = XS[self.sampleName] if self.sampleName in XS else 0.
        self.nevents = EV[self.sampleName] if self.sampleName in EV else 0.
        self.xsWeight = self.xs / self.nevents if self.nevents > 0 else 1.
        self.lumiWeight = self.xsWeight * self.lumi if self.isMC else 1.
        self.isLO = abs(self.nevents % 1) < 1.e-6 # if True, the event count is integer, so the weight should be normalized (+1)
        
        print "+ Module parameters: isMC", self.isMC, ", year", self.year, ", lumi", self.lumi, "pb"
        print "+ Sample", self.sampleName, ("is LO" if self.isLO else "is not LO"), ", XS", self.xs, ", events", self.nevents
        print "+ Weight", self.lumiWeight
        if self.isMC and self.isLO: print "+ Sample is LO, gen weight will be set to 1"
#        self.puTool = PileupWeightTool(year = year) if self.isMC else None

        self.SingleMuIsoTriggers = ["HLT_IsoMu24", "HLT_IsoTkMu24", "HLT_IsoMu27", "HLT_IsoTkMu27"]
        self.SingleMuTriggers = ["HLT_Mu50", "HLT_TkMu50", "HLT_Mu100", "HLT_TkMu100"]
        self.DoubleMuonTriggers = ["HLT_Mu17_Mu8", "HLT_Mu17_Mu8_DZ", "HLT_Mu17_TkMu8_DZ"]
        self.SingleEleIsoTriggers = ["HLT_Ele27_WPTight_Gsf", "HLT_Ele27_WPLoose_Gsf", "HLT_Ele32_WPTight_Gsf", "HLT_Ele35_WPTight_Gsf"]
        self.SingleEleTriggers = ["HLT_Ele105_CaloIdVT_GsfTrkIdT", "HLT_Ele115_CaloIdVT_GsfTrkIdT", "HLT_Photon175", "HLT_Photon200"]
        
        if self.isMC:
            self.muSFs  = MuonSFs(year = self.year)
            self.elSFs  = ElectronSFs(year = self.year)
            self.puTool = PileupWeightTool(year = self.year)
#            self.btagToolAK8 = BTagWeightTool('CSVv2','AK8','loose',sigma='central',channel='ll',year=year)
#            self.btagToolAK4 = BTagWeightTool('CSVv2','AK4','loose',sigma='central',channel='ll',year=year)
#            self.btagToolAK8_deep = BTagWeightTool('DeepCSV','AK8','loose',sigma='central',channel='ll',year=year)
#            self.btagToolAK8_deep_up = BTagWeightTool('DeepCSV','AK8','loose',sigma='up',channel='ll',year=year)
#            self.btagToolAK8_deep_down = BTagWeightTool('DeepCSV','AK8','loose',sigma='down',channel='ll',year=year)
#            self.btagToolAK4_deep = BTagWeightTool('DeepCSV','AK4','loose',sigma='central',channel='ll',year=year)
#            self.btagToolAK4_deep_up = BTagWeightTool('DeepCSV','AK4','loose',sigma='up',channel='ll',year=year)
#            self.btagToolAK4_deep_down = BTagWeightTool('DeepCSV','AK4','loose',sigma='down',channel='ll',year=year)
            if 'DYJetsToLL_M-50' in self.fileName: self.VptCorr = DYCorrection('DYJetsToLL')
            elif 'ZJetsToNuNu' in self.fileName: self.VptCorr = DYCorrection('ZJetsToNuNu')
            elif 'WJetsToLNu' in self.fileName: self.VptCorr = DYCorrection('WJetsToLNu')
            else: self.VptCorr = None
    
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        outputFile.mkdir("Hists")
        outputFile.cd("Hists")
        for histname, hist in self.hists.iteritems():
            hist.Write()
        outputFile.cd("..")
        print "+ File closed successfully"
        pass
        
    
    def analyze(self, event):
        iSkim = 0
        eventWeightLumi, lheWeight, stitchWeight, puWeight, qcdnloWeight, qcdnnloWeight, ewknloWeight, topWeight = 1., 1., 1., 1., 1., 1., 1., 1.
        triggerWeight, leptonWeight = 1., 1.
        MinMuonIso, MaxMuonIso, MinMuonMetDPhi, MaxMuonMetDPhi, MinMuonJetDR = -1., -1., -1., -1., -1.
        mZ, mW, mT, ptZ, ptW = -1., -1., -1., -1., -1.
        dEtaLL, dPhiLL, dRLL = -1., -1., -1.
        mJJ, ptJJ, dEtaJJ, dPhiJJ, dRJJ = -1., -1., -1., -1., -1.
        mLLJJ, mNJ = -1., -1.
        mHadW, mLepTop1, mLepTop2, mHadTop1, mHadTop2 = -1., -1., -1., -1., -1.
        isSingleMuIsoTrigger, isSingleMuTrigger, isDoubleMuonTrigger, isSingleEleIsoTrigger, isSingleEleTrigger = False, False, False, False, False
        for t in self.SingleMuIsoTriggers:
            if hasattr(event, t) and getattr(event, t): isSingleMuIsoTrigger = True
        for t in self.SingleMuTriggers:
            if hasattr(event, t) and getattr(event, t): isSingleMuTrigger = True
        for t in self.DoubleMuonTriggers:
            if hasattr(event, t) and getattr(event, t): isDoubleMuonTrigger = True
        for t in self.SingleEleIsoTriggers:
            if hasattr(event, t) and getattr(event, t): isSingleEleIsoTrigger = True
        for t in self.SingleEleTriggers:
            if hasattr(event, t) and getattr(event, t): isSingleEleTrigger = True
        
        
        
        
        lheWeight = 1.
        
        if self.isMC: 
            # Event weight
            if not self.isLO and hasattr(event, "LHEWeight_originalXWGTUP"): lheWeight = event.LHEWeight_originalXWGTUP
            
            GenVpt = self.VptCorr.getGenVpt(event) if not self.VptCorr is None else 0.
            
            # MC stitching weight
            
            # W+jets inclusive and exclusive
            if 'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' in self.fileName and 'Summer16' in self.fileName:
                if event.LHE_Vpt > 100.: stitchWeight = 0.
            
            # Z+jets and Z+gamma
            if self.fileName.startswith('ZGTo2LG_TuneCUETP8M1') or self.fileName.startswith('ZGToLLG_01J_5f_TuneCP5') or self.fileName.startswith('DYJetsToLL_M-50_Tune'):
                nGenPhotons = 0
                photonPtTh = 15. if self.fileName.startswith('ZGTo2LG_TuneCUETP8M1') or self.fileName.startswith('DYJetsToLL_M-50_TuneCUETP8M1') else 20.
                for i in range(event.nGenPart):
                    if GenPart_pdgId[i] == 22 and TMath.Odd(GenPart_statusFlags[i]) and GenPart_pt > photonPtTh:
                        nGenPhotons += 1
                if self.fileName.startswith('ZG') and nGenPhotons <= 0: stitchWeight = 0.
                if self.fileName.startswith('DYJetsToLL_M-50') and nGenPhotons >= 1: stitchWeight = 0.
            
            
            # PU weight
            puWeight = self.puTool.getWeight(event.Pileup_nTrueInt)
        
            # Higher order correction weights
            if not self.VptCorr is None:
                if not 'amcatnlo' in self.fileName: qcdnloWeight = self.VptCorr.getWeightQCDNLO(GenVpt)
                qcdnnloWeight = self.VptCorr.getWeightQCDNNLO(GenVpt)
                ewknloWeight = self.VptCorr.getWeightEWKNLO(GenVpt)
             
            if 'TTTo' in self.fileName:
                Top1_pt, Top2_pt = getTTPt(event)
                topWeight = getTTptWeight(Top1_pt, Top2_pt)
        
        self.hists["Events"].Fill(0, lheWeight)
        
#        electrons = Collection(event, "Electron")
#        muons = Collection(event, "Muon")
#        jets = Collection(event, "Jet")
#        eventSum = ROOT.TLorentzVector()

#        #select events with at least 2 muons
#        if len(muons) >=2 :
#          for lep in muons :     #loop on muons
#                  eventSum += lep.p4()
#          for lep in electrons : #loop on electrons
#            eventSum += lep.p4()
#          for j in jets :       #loop on jets
#            eventSum += j.p4()

        # Clean collections
        
        # Electrons
        cleanElectron = []
        for i in range(event.nElectron):
            if event.Electron_pt[i] > 10. and event.Electron_cutBased[i] >= 2:
                p4 = TLorentzVector()
                p4.SetPtEtaPhiM(event.Electron_pt[i], event.Electron_eta[i], event.Electron_phi[i], event.Electron_mass[i])
                cleanElectron.append(p4)
        
        # Muons
        cleanMuon = []
        for i in range(event.nMuon):
            if event.Muon_pt[i] > 10. and event.Muon_mediumId[i] and event.Muon_pfRelIso03_all[i] < 0.15:
                p4 = TLorentzVector()
                p4.SetPtEtaPhiM(event.Muon_pt[i], event.Muon_eta[i], event.Muon_phi[i], event.Muon_mass[i])
                cleanMuon.append(p4)
        
        # Jets and Event variables
        cleanJet, cleanBJet, cleanNonBJet = [], [], []
        HT30, Nj20, Nj30, Nj40, nBJet = 0., 0, 0, 0, 0
        CSVs = []
        twoJets, allJets = TLorentzVector(), TLorentzVector()
        for i in range(event.nJet):
            if event.Jet_jetId[i] >= 6 and abs(event.Jet_eta[i]) < 2.5:
                p4 = TLorentzVector()
                p4.SetPtEtaPhiM(event.Jet_pt[i], event.Jet_eta[i], event.Jet_phi[i], event.Jet_mass[i])
                # remove overlaps with electrons and muons
                cleanFromLeptons = True
                for e in range(len(cleanElectron)):
                    if cleanElectron[e].DeltaR(p4) < 0.4: cleanFromLeptons = False
                for m in range(len(cleanMuon)):
                    if cleanMuon[m].DeltaR(p4) < 0.4: cleanFromLeptons = False
                # fill variables
                if cleanFromLeptons:
                    if event.Jet_pt[i] > 20.:
                        Nj20 += 1
                    if event.Jet_pt[i] > 30.:
                        HT30 += event.Jet_pt[i]
                        Nj30 += 1
                        cleanJet.append(p4)
                        if event.Jet_btagDeepB[i] >= self.btagMedium: cleanBJet.append(p4)
                        else: cleanNonBJet.append(p4)
                        CSVs.append([i, event.Jet_btagDeepB[i]])
                        if len(cleanJet) < 2: twoJets += p4
                        allJets += p4
                    if event.Jet_pt[i] > 40.:
                        Nj40 += 1

                
        # b-tag ranking
        nBJet = len(cleanBJet)
        CSV1, CSV2, CSV3, CSV4, iCSV1, iCSV2, iCSV3, iCSV4 = 0., 0., 0., 0., -1, -1, -1, -1
        
        CSVs.sort(key=lambda x : x[1], reverse=True)
        if len(CSVs) > 0: iCSV1, CSV1 = CSVs[0][0], CSVs[0][1]
        if len(CSVs) > 1: iCSV2, CSV2 = CSVs[1][0], CSVs[1][1]
        if len(CSVs) > 2: iCSV3, CSV3 = CSVs[2][0], CSVs[2][1]
        if len(CSVs) > 3: iCSV4, CSV4 = CSVs[3][0], CSVs[3][1]
        
        if len(cleanJet) >= 2:
            mJJ = (cleanJet[0] + cleanJet[1]).M()
            ptJJ = (cleanJet[0] + cleanJet[1]).Pt()
            dEtaJJ = abs(cleanJet[0].Eta() - cleanJet[1].Eta())
            dPhiJJ = abs(cleanJet[0].DeltaPhi(cleanJet[1]))
            dRJJ = cleanJet[0].DeltaR(cleanJet[1])
        mNJ = allJets.M()
        
        Lepton1, Lepton2, Lepton3, Neutrino, MET, LLJJ, Vis = TLorentzVector(), TLorentzVector(), TLorentzVector(), TLorentzVector(), TLorentzVector(), TLorentzVector(), TLorentzVector()
        MET.SetPtEtaPhiM(event.MET_pt, 0., event.MET_phi, 0.)
        
        # Categorization:
        # iSkim = 1: 2 muons (OS or SS)
        # iSkim = 2: 1 muon and 1 electron (no OS requirement)
        # iSkim = 3: 3 muons (assumed that they are not 3 same-sign)
        # iSkim = 4: 2 muons (OS) and 1 electron
        # iSkim = 5: 1 muons, 3 jets, >= 1 btag
        # iSkim = 6: 2 electrons
        
        # case 3a: 3 lepton CR (3mu)
        if iSkim == 0 and event.nMuon >= 3:
            if (isSingleMuIsoTrigger or isSingleMuTrigger) and event.Muon_pt[0] > 27. and event.Muon_pt[1] > 15. and event.Muon_pt[2] > 15. and event.Muon_mediumId[0] and event.Muon_mediumId[1] and event.Muon_mediumId[2]:
                Lepton1.SetPtEtaPhiM(event.Muon_pt[0], event.Muon_eta[0], event.Muon_phi[0], event.Muon_mass[0])
                Lepton2.SetPtEtaPhiM(event.Muon_pt[1], event.Muon_eta[1], event.Muon_phi[1], event.Muon_mass[1])
                Lepton3.SetPtEtaPhiM(event.Muon_pt[2], event.Muon_eta[2], event.Muon_phi[2], event.Muon_mass[2])
                if event.Muon_charge[0]*event.Muon_charge[1] < 0:
                    mll = (Lepton1 + Lepton2).M()
                    ptll = (Lepton1 + Lepton2).Pt()
                    detall = abs(Lepton1.Eta() - Lepton2.Eta())
                    dphill = abs(Lepton1.DeltaPhi(Lepton2))
                    drll = Lepton1.DeltaR(Lepton2)
                else:
                    mll = (Lepton1 + Lepton3).M()
                    ptll = (Lepton1 + Lepton3).Pt()
                    detall = abs(Lepton1.Eta() - Lepton3.Eta())
                    dphill = abs(Lepton1.DeltaPhi(Lepton3))
                    drll = Lepton1.DeltaR(Lepton3)
                if mll > 15.:
                    iSkim = 3
                    # Variables
                    mZ, ptZ = mll, ptll
                    dEtaLL, dPhiLL, dRLL = detall, dphill, drll
                    MinMuonIso = min(min(event.Muon_pfRelIso03_all[0], event.Muon_pfRelIso03_all[1]), event.Muon_pfRelIso03_all[2])
                    MaxMuonIso = max(max(event.Muon_pfRelIso03_all[0], event.Muon_pfRelIso03_all[1]), event.Muon_pfRelIso03_all[2])
                    MinMuonMetDPhi = min(min(abs(Lepton1.DeltaPhi(MET)), abs(Lepton2.DeltaPhi(MET))), abs(Lepton3.DeltaPhi(MET)))
                    MaxMuonMetDPhi = max(max(abs(Lepton1.DeltaPhi(MET)), abs(Lepton2.DeltaPhi(MET))), abs(Lepton3.DeltaPhi(MET)))
                    MinMuonJetDR = min(min(getMinMuonJetDR(cleanJet, Lepton1), getMinMuonJetDR(cleanJet, Lepton2)), getMinMuonJetDR(cleanJet, Lepton3))
                    LLJJ = twoJets + Lepton1 + Lepton2
                    Vis = allJets + Lepton1 + Lepton2 + Lepton3
                    # Weights
                    if self.isMC:
                        triggerWeight = self.muSFs.getTriggerSF(event.Muon_pt[0], event.Muon_eta[0])
                        IdSF1 = self.muSFs.getIdSF(event.Muon_pt[0], event.Muon_eta[0], 2)
                        IsoSF1 = self.muSFs.getIsoSF(event.Muon_pt[0], event.Muon_eta[0])
                        IdSF2 = self.muSFs.getIdSF(event.Muon_pt[1], event.Muon_eta[1], 2)
                        IsoSF2 = self.muSFs.getIsoSF(event.Muon_pt[1], event.Muon_eta[1])
                        IdSF3 = self.muSFs.getIdSF(event.Muon_pt[2], event.Muon_eta[2], 2)
                        IsoSF3 = self.muSFs.getIsoSF(event.Muon_pt[2], event.Muon_eta[2])
                        leptonWeight = IdSF1 * IsoSF1 * IdSF2 * IsoSF2 * IdSF3 * IsoSF3
        
        # case 3b: 3 lepton CR (2mu 1e)
        if iSkim == 0 and event.nMuon >= 2 and event.nElectron >= 1:
            if (isSingleMuIsoTrigger or isSingleMuTrigger) and event.Muon_pt[0] > 27. and event.Muon_pt[1] > 15. and event.Electron_pt[0] > 15. and event.Muon_mediumId[0] and event.Muon_mediumId[1] and event.Electron_cutBased[0] >= 2 and event.Muon_charge[0]*event.Muon_charge[1] < 0:
                Lepton1.SetPtEtaPhiM(event.Muon_pt[0], event.Muon_eta[0], event.Muon_phi[0], event.Muon_mass[0])
                Lepton2.SetPtEtaPhiM(event.Muon_pt[1], event.Muon_eta[1], event.Muon_phi[1], event.Muon_mass[1])
                Lepton3.SetPtEtaPhiM(event.Electron_pt[0], event.Electron_eta[0], event.Electron_phi[0], event.Electron_mass[0])
                mll = (Lepton1 + Lepton2).M()
                ptll = (Lepton1 + Lepton2).Pt()
                if mll > 15.:
                    iSkim = 4
                    # Variables
                    mZ, ptZ = mll, ptll
                    dEtaLL = abs(Lepton1.Eta() - Lepton2.Eta())
                    dPhiLL = abs(Lepton1.DeltaPhi(Lepton2))
                    dRLL = Lepton1.DeltaR(Lepton2)
                    MinMuonIso = min(event.Muon_pfRelIso03_all[0], event.Muon_pfRelIso03_all[1])
                    MaxMuonIso = max(event.Muon_pfRelIso03_all[0], event.Muon_pfRelIso03_all[1])
                    MinMuonMetDPhi = min(min(abs(Lepton1.DeltaPhi(MET)), abs(Lepton2.DeltaPhi(MET))), abs(Lepton3.DeltaPhi(MET)))
                    MaxMuonMetDPhi = max(max(abs(Lepton1.DeltaPhi(MET)), abs(Lepton2.DeltaPhi(MET))), abs(Lepton3.DeltaPhi(MET)))
                    MinMuonJetDR = min(getMinMuonJetDR(cleanJet, Lepton1), getMinMuonJetDR(cleanJet, Lepton2))
                    LLJJ = twoJets + Lepton1 + Lepton2
                    Vis = allJets + Lepton1 + Lepton2 + Lepton3
                    # Weights
                    if self.isMC:
                        triggerWeight = self.muSFs.getTriggerSF(event.Muon_pt[0], event.Muon_eta[0])
                        IdSF1 = self.muSFs.getIdSF(event.Muon_pt[0], event.Muon_eta[0], 2)
                        IsoSF1 = self.muSFs.getIsoSF(event.Muon_pt[0], event.Muon_eta[0])
                        IdSF2 = self.muSFs.getIdSF(event.Muon_pt[1], event.Muon_eta[1], 2)
                        IsoSF2 = self.muSFs.getIsoSF(event.Muon_pt[1], event.Muon_eta[1])
                        IdIsoSF3 = self.elSFs.getIdIsoSF(event.Electron_pt[0], event.Electron_eta[0])
                        leptonWeight = IdSF1 * IsoSF1 * IdSF2 * IsoSF2 * IdIsoSF3
        
        # case 1: Z->mumu CR (2 mu)
        if iSkim == 0 and event.nMuon >= 2:
            if (isSingleMuIsoTrigger or isSingleMuTrigger) and event.Muon_pt[0] > 27. and event.Muon_pt[1] > 7. and event.Muon_mediumId[0] and event.Muon_mediumId[1]:
                Lepton1.SetPtEtaPhiM(event.Muon_pt[0], event.Muon_eta[0], event.Muon_phi[0], event.Muon_mass[0])
                Lepton2.SetPtEtaPhiM(event.Muon_pt[1], event.Muon_eta[1], event.Muon_phi[1], event.Muon_mass[1])
                mll = (Lepton1 + Lepton2).M()
                ptll = (Lepton1 + Lepton2).Pt()
                if mll > 15.:
                    iSkim = 1
                    # Variables
                    mZ, ptZ = mll, ptll
                    dEtaLL = abs(Lepton1.Eta() - Lepton2.Eta())
                    dPhiLL = abs(Lepton1.DeltaPhi(Lepton2))
                    dRLL = Lepton1.DeltaR(Lepton2)
                    MinMuonIso = min(event.Muon_pfRelIso03_all[0], event.Muon_pfRelIso03_all[1])
                    MaxMuonIso = max(event.Muon_pfRelIso03_all[0], event.Muon_pfRelIso03_all[1])
                    MinMuonMetDPhi = min(abs(Lepton1.DeltaPhi(MET)), abs(Lepton2.DeltaPhi(MET)))
                    MaxMuonMetDPhi = max(abs(Lepton1.DeltaPhi(MET)), abs(Lepton2.DeltaPhi(MET)))
                    MinMuonJetDR = min(getMinMuonJetDR(cleanJet, Lepton1), getMinMuonJetDR(cleanJet, Lepton2))
                    LLJJ = twoJets + Lepton1 + Lepton2
                    Vis = allJets + Lepton1 + Lepton2
                    # Weights
                    if self.isMC:
                        triggerWeight = self.muSFs.getTriggerSF(event.Muon_pt[0], event.Muon_eta[0])
                        IdSF1 = self.muSFs.getIdSF(event.Muon_pt[0], event.Muon_eta[0], 2)
                        IdSF2 = self.muSFs.getIdSF(event.Muon_pt[1], event.Muon_eta[1], 2)
                        IsoSF1 = self.muSFs.getIsoSF(event.Muon_pt[0], event.Muon_eta[0])
                        IsoSF2 = self.muSFs.getIsoSF(event.Muon_pt[1], event.Muon_eta[1])
                        leptonWeight = IdSF1 * IdSF2 * IsoSF1 * IsoSF2
        
        # case 4: Z->ee CR (2 electrons)
        if iSkim == 0 and event.nElectron >= 2:
            if isSingleEleIsoTrigger and event.Electron_pt[0] > 35. and event.Electron_pt[1] > 10. and event.Electron_cutBased[0] > 0 and event.Electron_cutBased[1] > 0:
                Lepton1.SetPtEtaPhiM(event.Electron_pt[0], event.Electron_eta[0], event.Electron_phi[0], event.Electron_mass[0])
                Lepton2.SetPtEtaPhiM(event.Electron_pt[1], event.Electron_eta[1], event.Electron_phi[1], event.Electron_mass[1])
                mll = (Lepton1 + Lepton2).M()
                ptll = (Lepton1 + Lepton2).Pt()
                if mll > 15.:
                    iSkim = 6
                    # Variables
                    mZ, ptZ = mll, ptll
                    dEtaLL = abs(Lepton1.Eta() - Lepton2.Eta())
                    dPhiLL = abs(Lepton1.DeltaPhi(Lepton2))
                    dRLL = Lepton1.DeltaR(Lepton2)
                    MinMuonIso = event.Electron_pfRelIso03_all[0]
                    MaxMuonIso = event.Electron_pfRelIso03_all[0]
                    MinMuonMetDPhi = min(abs(Lepton1.DeltaPhi(MET)), abs(Lepton2.DeltaPhi(MET)))
                    MaxMuonMetDPhi = max(abs(Lepton1.DeltaPhi(MET)), abs(Lepton2.DeltaPhi(MET)))
                    MinMuonJetDR = min(getMinMuonJetDR(cleanJet, Lepton1), getMinMuonJetDR(cleanJet, Lepton2))
                    LLJJ = twoJets + Lepton1 + Lepton2
                    Vis = allJets + Lepton1 + Lepton2
                    # Weights
                    if self.isMC:
                        triggerWeight = self.elSFs.getTriggerSF(event.Electron_pt[0], event.Electron_eta[0])
                        leptonWeight = self.elSFs.getIdIsoSF(event.Electron_pt[0], event.Electron_eta[0]) * self.elSFs.getIdIsoSF(event.Electron_pt[1], event.Electron_eta[1])
        
        # case 2: ttbar and Z OF CR (1 muon and 1 electron)
        if iSkim == 0 and event.nMuon >= 1 and event.nElectron >= 1:
            if (isSingleMuIsoTrigger or isSingleMuTrigger) and event.Muon_pt[0] > 27. and event.Electron_pt[0] > 20. and event.Muon_mediumId[0] and event.Electron_cutBased[0] >= 2:
                Lepton1.SetPtEtaPhiM(event.Muon_pt[0], event.Muon_eta[0], event.Muon_phi[0], event.Muon_mass[0])
                Lepton2.SetPtEtaPhiM(event.Electron_pt[0], event.Electron_eta[0], event.Electron_phi[0], event.Electron_mass[0])
                mll = (Lepton1 + Lepton2).M()
                ptll = (Lepton1 + Lepton2).Pt()
                if mll > 15.:
                    iSkim = 2
                    # Variables
                    mZ, ptZ = mll, ptll
                    dEtaLL = abs(Lepton1.Eta() - Lepton2.Eta())
                    dPhiLL = abs(Lepton1.DeltaPhi(Lepton2))
                    dRLL = Lepton1.DeltaR(Lepton2)
                    MinMuonIso = event.Muon_pfRelIso03_all[0]
                    MaxMuonIso = event.Muon_pfRelIso03_all[0]
                    MinMuonMetDPhi = abs(Lepton1.DeltaPhi(MET))
                    MaxMuonMetDPhi = abs(Lepton1.DeltaPhi(MET))
                    MinMuonJetDR = min(getMinMuonJetDR(cleanJet, Lepton1), getMinMuonJetDR(cleanJet, Lepton2))
                    LLJJ = twoJets + Lepton1 + Lepton2
                    Vis = allJets + Lepton1 + Lepton2
                    # Weights
                    if self.isMC:
                        triggerWeight = self.muSFs.getTriggerSF(Lepton1.Pt(), Lepton1.Eta())
                        IdSF1 = self.muSFs.getIdSF(event.Muon_pt[0], event.Muon_eta[0], 2)
                        IsoSF1 = self.muSFs.getIsoSF(event.Muon_pt[0], event.Muon_eta[0])
                        IdIsoSF2 = self.elSFs.getIdIsoSF(event.Electron_pt[0], event.Electron_eta[0])
                        leptonWeight = IdSF1 * IsoSF1 * IdIsoSF2
        
        # case 4: ttbar CR (1 muon and >= 3 jets)
        if iSkim == 0 and event.nMuon >= 1:
            if (isSingleMuIsoTrigger or isSingleMuTrigger) and event.Muon_pt[0] > 27. and event.Muon_mediumId[0] and event.Muon_pfRelIso03_all[0] < 0.15:
                Lepton1.SetPtEtaPhiM(event.Muon_pt[0], event.Muon_eta[0], event.Muon_phi[0], event.Muon_mass[0])
                pzN = recoverNeutrinoPz(Lepton1, MET)
                Neutrino.SetPxPyPzE(MET.Px(), MET.Py(), pzN, MET.Pt())
                mW = (Lepton1 + Neutrino).M()
                ptW = (Lepton1 + Neutrino).Pt()
                mT = math.sqrt(2. * Lepton1.Pt() * MET.Pt() * (1.-math.cos(Lepton1.DeltaPhi(MET))))
                if Nj30 >= 3: # and nBJet >= 1:
                    iSkim = 5
                    # Variables
                    MinMuonIso = event.Muon_pfRelIso03_all[0]
                    MaxMuonIso = event.Muon_pfRelIso03_all[0]
                    MinMuonMetDPhi = abs(Lepton1.DeltaPhi(MET))
                    MaxMuonMetDPhi = abs(Lepton1.DeltaPhi(MET))
                    MinMuonJetDR = getMinMuonJetDR(cleanJet, Lepton1)
                    LLJJ = twoJets + Lepton1
                    Vis = allJets + Lepton1
                    # W and Top reconstruction
                    if len(cleanBJet) >= 2:
                        mLepTop1 = (Lepton1 + Neutrino + cleanBJet[0]).M()
                        mLepTop2 = (Lepton1 + Neutrino + cleanBJet[1]).M()
                    elif len(cleanBJet) >= 1:
                        mLepTop1 = (Lepton1 + Neutrino + cleanBJet[0]).M()
                        mHadTop2 = mHadTop1
                    if len(cleanNonBJet) >= 2:
                        mHadW = (cleanNonBJet[0] + cleanNonBJet[1]).M()
                        if len(cleanBJet) >= 2:
                            mHadTop1 = (cleanNonBJet[0] + cleanNonBJet[1] + cleanBJet[0]).M()
                            mHadTop2 = (cleanNonBJet[0] + cleanNonBJet[1] + cleanBJet[1]).M()
                        elif len(cleanBJet) >= 1:
                            mHadTop1 = (cleanNonBJet[0] + cleanNonBJet[1] + cleanBJet[0]).M()
                            mHadTop2 = mHadTop1
                    # Weights
                    if self.isMC:
                        triggerWeight = self.muSFs.getTriggerSF(Lepton1.Pt(), Lepton1.Eta())
                        IdSF1 = self.muSFs.getIdSF(event.Muon_pt[0], event.Muon_eta[0], 2)
                        IsoSF1 = self.muSFs.getIsoSF(event.Muon_pt[0], event.Muon_eta[0])
                        leptonWeight = IdSF1 * IsoSF1
        
        passedMETFilters = True
        filters = ["Flag_goodVertices", "Flag_globalSuperTightHalo2016Filter", "Flag_BadPFMuonFilter", "Flag_EcalDeadCellTriggerPrimitiveFilter", "Flag_HBHENoiseFilter", "Flag_HBHENoiseIsoFilter", "Flag_ecalBadCalibFilter", "Flag_ecalBadCalibFilterV2"]
        if not self.isMC: filters += ["Flag_eeBadScFilter"]
        for f in filters:
            if hasattr(event, f) and getattr(event, f) == False: passedMETFilters = False
#        try:
##            if event.Flag_goodVertices: print "Flag_goodVertices"
##            if event.Flag_globalSuperTightHalo2016Filter: print "Flag_globalSuperTightHalo2016Filter"
##            if event.Flag_BadPFMuonFilter: print "Flag_BadPFMuonFilter"
##            if event.Flag_EcalDeadCellTriggerPrimitiveFilter: print "Flag_EcalDeadCellTriggerPrimitiveFilter"
##            if event.Flag_HBHENoiseFilter: print "Flag_HBHENoiseFilter"
##            if event.Flag_HBHENoiseIsoFilter: print "Flag_HBHENoiseIsoFilter"
###            if (self.isMC or event.Flag_eeBadScFilter): print "Flag_eeBadScFilter"
##            if event.Flag_ecalBadCalibFilter: print "Flag_ecalBadCalibFilterV2"
#            if event.Flag_goodVertices and event.Flag_globalSuperTightHalo2016Filter and event.Flag_BadPFMuonFilter and event.Flag_EcalDeadCellTriggerPrimitiveFilter and event.Flag_HBHENoiseFilter and event.Flag_HBHENoiseIsoFilter: # and event.Flag_ecalBadCalibFilter: #and (self.isMC or event.Flag_eeBadScFilter): FIXME
#                passedMETFilters = True
##            if not self.isMC:
##                if not event.Flag_eeBadScFilter:
##                    passedMETFilters = False
#        except:
#            passedMETFilters = False
        
        if iSkim == 0: return False
        
        if self.isMC: eventWeightLumi = self.lumiWeight * lheWeight * puWeight * topWeight * qcdnloWeight * qcdnnloWeight * ewknloWeight * triggerWeight * leptonWeight
        
        self.out.fillBranch("iSkim", iSkim)
        self.out.fillBranch("isMC", self.isMC)
        self.out.fillBranch("isSingleMuIsoTrigger", isSingleMuIsoTrigger)
        self.out.fillBranch("isSingleMuTrigger", isSingleMuTrigger)
        self.out.fillBranch("isDoubleMuonTrigger", isDoubleMuonTrigger)
        self.out.fillBranch("isSingleEleIsoTrigger", isSingleEleIsoTrigger)
        self.out.fillBranch("isSingleEleTrigger", isSingleEleTrigger)
        self.out.fillBranch("passedMETFilters", passedMETFilters)
        self.out.fillBranch("nCleanElectron", len(cleanElectron))
        self.out.fillBranch("nCleanMuon", len(cleanMuon))
        self.out.fillBranch("nCleanJet", len(cleanJet))
        self.out.fillBranch("Z_mass", mZ)
        self.out.fillBranch("Z_pt", ptZ)
        self.out.fillBranch("W_mass", mW)
        self.out.fillBranch("W_tmass", mT)
        self.out.fillBranch("W_pt", ptW)
        self.out.fillBranch("ll_dEta", dEtaLL)
        self.out.fillBranch("ll_dPhi", dPhiLL)
        self.out.fillBranch("ll_dR", dRLL)
        self.out.fillBranch("Wqq_mass", mHadW)
        self.out.fillBranch("Tlvb1_mass", mLepTop1)
        self.out.fillBranch("Tlvb2_mass", mLepTop2)
        self.out.fillBranch("Tqqb1_mass", mHadTop1)
        self.out.fillBranch("Tqqb2_mass", mHadTop2)
        self.out.fillBranch("jj_mass", mJJ)
        self.out.fillBranch("jj_pt", ptJJ)
        self.out.fillBranch("jj_dEta", dEtaJJ)
        self.out.fillBranch("jj_dPhi", dPhiJJ)
        self.out.fillBranch("jj_dR", dRJJ)
        self.out.fillBranch("nj_mass", mNJ)
        self.out.fillBranch("vis_mass", Vis.M())
        self.out.fillBranch("lljj_mass", LLJJ.M())
        self.out.fillBranch("minMuonIso", MinMuonIso)
        self.out.fillBranch("maxMuonIso", MaxMuonIso)
        self.out.fillBranch("minMuonMetDPhi", MinMuonMetDPhi)
        self.out.fillBranch("maxMuonMetDPhi", MaxMuonMetDPhi)
        self.out.fillBranch("minMuonJetDR", MinMuonJetDR)
        self.out.fillBranch("HT30", HT30)
        self.out.fillBranch("nj20", Nj20)
        self.out.fillBranch("nj30", Nj30)
        self.out.fillBranch("nj40", Nj40)
        self.out.fillBranch("nBJet", nBJet)
        self.out.fillBranch("CSV1", CSV1)
        self.out.fillBranch("CSV2", CSV2)
        self.out.fillBranch("CSV3", CSV3)
        self.out.fillBranch("CSV4", CSV4)
        self.out.fillBranch("iCSV1", iCSV1)
        self.out.fillBranch("iCSV2", iCSV2)
        self.out.fillBranch("iCSV3", iCSV3)
        self.out.fillBranch("iCSV4", iCSV4)
        self.out.fillBranch("lumiWeight", self.lumiWeight)
        self.out.fillBranch("lheWeight", lheWeight)
        self.out.fillBranch("stitchWeight", stitchWeight)
        self.out.fillBranch("puWeight", puWeight)
        self.out.fillBranch("topWeight", topWeight)
        self.out.fillBranch("qcdnloWeight", qcdnloWeight)
        self.out.fillBranch("qcdnnloWeight", qcdnnloWeight)
        self.out.fillBranch("ewknloWeight", ewknloWeight)
        self.out.fillBranch("triggerWeight", triggerWeight)
        self.out.fillBranch("leptonWeight", leptonWeight)
        self.out.fillBranch("eventWeightLumi", eventWeightLumi)
        
        return True


