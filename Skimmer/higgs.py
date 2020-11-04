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
#from CorrectionTools.RecoilCorrectionTool import getTTptWeight, getTTPt
#from CorrectionTools.DYCorrection import *
#from PileupWeightTool import PileupWeightTool
#from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeightProducer

from ROOT import TLorentzVector, TVector3, TVector2
from utils import EV_v7, XS, getNameFromFile

class Higgs(Module):
    def __init__(self):
        self.writeHistFile=True
        


    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
        self.event = 0
        self.hists = {}
        self.hists["Nevents"] = ROOT.TH1F("Nevents", "Nevents", 1, 0, 1)
        self.hists["Acceptance"] = ROOT.TH1F("Acceptance", "Acceptance", 5, -0.5, 4.5)
        self.hists["genH_pt"] = ROOT.TH1F("genH_pt", ";generator H p_{T} (GeV)", 100, 0., 100.)
        self.hists["genH_eta"] = ROOT.TH1F("genH_eta", ";generator H #eta", 100, -5., 5.)
        self.hists["genJPsi_pt"] = ROOT.TH1F("genJPsi_pt", ";generator J/#Psi p_{T} (GeV)", 100, 0., 100.)
        self.hists["genJPsi_eta"] = ROOT.TH1F("genJPsi_eta", ";generator J/#Psi #eta", 100, -5., 5.)
        self.hists["genPhoton_pt"] = ROOT.TH1F("genPhoton_pt", ";generator #gamma p_{T} (GeV)", 100, 0., 100.)
        self.hists["genPhoton_eta"] = ROOT.TH1F("genPhoton_eta", ";generator #gamma #eta", 100, -5., 5.)
        self.hists["genMuon1_pt"] = ROOT.TH1F("genMuon1_pt", ";generator #mu^{-} p_{T} (GeV)", 100, 0., 100.)
        self.hists["genMuon1_eta"] = ROOT.TH1F("genMuon1_eta", ";generator #mu^{-} #eta", 100, -5., 5.)
        self.hists["genMuon2_pt"] = ROOT.TH1F("genMuon2_pt", ";generator #mu^{+} p_{T} (GeV)", 100, 0., 100.)
        self.hists["genMuon2_eta"] = ROOT.TH1F("genMuon2_eta", ";generator #mu^{+} #eta", 100, -5., 5.)
        
        self.hists["genCosThetaStar"] = ROOT.TH1F("genCosThetaStar", ";cos #theta^{*}", 100, -1., 1.)
        self.hists["genCosTheta1"] = ROOT.TH1F("genCosTheta1", ";cos #theta_{1}", 100, -1., 1.)
        self.hists["genPhi1"] = ROOT.TH1F("genPhi1", ";#Phi_{1}", 100, -3.1415, 3.1415)
        
        self.hists["Cutflow"] = ROOT.TH1F("Cutflow", "Cutflow", 10, -0.5, 9.5)
        self.hists["Cutflow"].GetXaxis().SetBinLabel(1, "All events")
        self.hists["Cutflow"].GetXaxis().SetBinLabel(2, "Acceptance")
        self.hists["Cutflow"].GetXaxis().SetBinLabel(3, "2 reco muons")
        self.hists["Cutflow"].GetXaxis().SetBinLabel(4, "J/#Psi cand")
        self.hists["Cutflow"].GetXaxis().SetBinLabel(5, "reco #gamma")
#        self.addObject(self.h_events)
#        self.h_events.SetDirectory
        self.verbose = -1
    
    def endJob(self):
        Module.endJob(self)
        print "+ Module ended successfully,"#, self.h_events.GetEntries(), "events analyzed"
        pass
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("isMC", "I")
        self.out.branch("is2016", "I")
        self.out.branch("is2017", "I")
        self.out.branch("is2018", "I")
        self.out.branch("isSingleMuonTrigger", "I")
        self.out.branch("isSingleMuonPhotonTrigger", "I")
        self.out.branch("isSingleMuonNoFiltersPhotonTrigger", "I")
        self.out.branch("isDoubleMuonTrigger", "I")
        self.out.branch("isDoubleMuonPhotonTrigger", "I")
        self.out.branch("isJPsiTrigger", "I")
        self.out.branch("isDisplacedTrigger", "I")
        self.out.branch("passedMETFilters", "I")
        self.out.branch("nCleanElectron", "I")
        self.out.branch("nCleanMuon", "I")
        self.out.branch("nCleanTau", "I")
        self.out.branch("nCleanPhoton", "I")
        self.out.branch("nCleanJet", "I")
        self.out.branch("nCleanBTagJet", "I")
        self.out.branch("HT30", "F")
        self.out.branch("iPhoton", "I")
        self.out.branch("iMuon1", "I")
        self.out.branch("iMuon2", "I")
        self.out.branch("JPsi_pt", "F")
        self.out.branch("JPsi_eta", "F")
        self.out.branch("JPsi_phi", "F")
        self.out.branch("JPsi_mass", "F")
        self.out.branch("JPsi_dEta", "F")
        self.out.branch("JPsi_dPhi", "F")
        self.out.branch("JPsi_dR", "F")
        self.out.branch("H_pt", "F")
        self.out.branch("H_eta", "F")
        self.out.branch("H_phi", "F")
        self.out.branch("H_mass", "F")
        self.out.branch("H_dEta", "F")
        self.out.branch("H_dPhi", "F")
        self.out.branch("H_dR", "F")
        self.out.branch("minMuonIso", "F")
        self.out.branch("maxMuonIso", "F")
        self.out.branch("minMuonMetDPhi", "F")
        self.out.branch("maxMuonMetDPhi", "F")
        self.out.branch("photonMetDPhi", "F")
        self.out.branch("metPlusPhotonDPhi", "F")
        self.out.branch("cosThetaStar", "F")
        self.out.branch("cosTheta1", "F")
        self.out.branch("phi1", "F")
        self.out.branch("lumiWeight", "F")
        self.out.branch("lheWeight", "F")
        self.out.branch("stitchWeight", "F")
        self.out.branch("puWeight", "F")
        self.out.branch("topWeight", "F")
        self.out.branch("qcdnloWeight", "F")
        self.out.branch("qcdnnloWeight", "F")
        self.out.branch("ewknloWeight", "F")
        self.out.branch("triggerWeight", "F")
        self.out.branch("leptonWeight", "F")
        self.out.branch("eventWeightLumi", "F")
        
        
        self.fileName = inputFile.GetName()
        self.sampleName = getNameFromFile(self.fileName)
        
        self.isMC = not "Run201" in self.fileName
        
        if self.verbose >= 0: print "+ Opening file", self.fileName
        
        self.thMuons = [10., 3.]
        self.thPhoton = [10.]
        
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
            if self.verbose >= 0: print "- Unknown year, aborting module"
            import sys
            sys.exit()
        
        self.xs = XS[self.sampleName] if self.sampleName in XS else 0.
        self.nevents = EV_v7[self.sampleName] if self.sampleName in EV_v7 else 0.
        self.xsWeight = self.xs / self.nevents if self.nevents > 0 else 1.
        self.lumiWeight = self.xsWeight * self.lumi if self.isMC else 1.
        self.isLO = abs(self.nevents % 1) < 1.e-6 # if True, the event count is integer, so the weight should be normalized (+1)
        self.isSignal = ('JPsiG' in self.sampleName)
        
        if self.verbose >= 1: print "+ Module parameters: isMC", self.isMC, ", year", self.year, ", lumi", self.lumi, "pb"
        if self.verbose >= 1: print "+ Sample", self.sampleName, ", XS", self.xs, ", events", self.nevents
        if self.verbose >= 1: print "+ Weight", self.lumiWeight
        if self.isMC and self.isLO and self.verbose >= 1: print "+ Sample is LO, gen weight will be set to 1"
#        self.puTool = PileupWeightTool(year = year) if self.isMC else None

        self.SingleMuonTriggers = ["HLT_IsoMu27"]
        self.SingleMuonPhotonTriggers = ["HLT_Mu17_Photon30_CaloIdL_L1ISO", "HLT_Mu17_Photon30_IsoCaloId", "HLT_Mu17_Photon30_CaloIdL"] # 27.13 in 2017
        self.SingleMuonNoFiltersPhotonTriggers = ["HLT_Mu38NoFiltersNoVtxDisplaced_Photon38_CaloIdL", "HLT_Mu38NoFiltersNoVtx_Photon38_CaloIdL", "HLT_Mu43NoFiltersNoVtx_Photon43_CaloIdL"]
        self.DoubleMuonTriggers = ["HLT_Mu17_Mu8", "HLT_Mu17_Mu8_DZ", "HLT_Mu17_TkMu8_DZ", "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass", "HLT_Mu37_TkMu27", ] #, "HLT_DoubleMu33NoFiltersNoVtxDisplaced"]
        self.DoubleMuonPhotonTriggers = ["HLT_DoubleMu20_7_Mass0to30_Photon23"]
        self.JPsiTriggers = ["HLT_Dimuon16_Jpsi", "HLT_Dimuon18_PsiPrime", "HLT_Dimuon18_PsiPrime_noCorrL1", "HLT_Dimuon25_Jpsi", "HLT_Dimuon25_Jpsi_noCorrL1", "HLT_Dimuon20_Jpsi", ]
        self.DisplacedTriggers = ["HLT_DoubleMu4_JpsiTrk_Displaced", "HLT_DoubleMu4_PsiPrimeTrk_Displaced"]
        
        if self.isMC:
            self.muSFs  = MuonSFs(year = self.year)
            self.elSFs  = ElectronSFs(year = self.year)
            self.puTool = PileupWeightTool(year = self.year)
    
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        outputFile.mkdir("Hists")
        outputFile.cd("Hists")
        for histname, hist in self.hists.iteritems():
            hist.Write()
        outputFile.cd("..")
        if self.verbose >= 0: print "+ File closed successfully"
        pass
        
    
    def analyze(self, event):
        eventWeightLumi, lheWeight, stitchWeight, puWeight, qcdnloWeight, qcdnnloWeight, ewknloWeight, topWeight = 1., 1., 1., 1., 1., 1., 1., 1.
        triggerWeight, leptonWeight = 1., 1.
        isSingleMuonTrigger, isSingleMuonPhotonTrigger, isSingleMuonNoFiltersPhotonTrigger, isDoubleMuonTrigger, isDoubleMuonPhotonTrigger, isJPsiTrigger, isDisplacedTrigger = False, False, False, False, False, False, False
        nCleanElectron, nCleanMuon, nCleanTau, nCleanPhoton, nCleanJet, nCleanBTagJet, HT30 = 0, 0, 0, 0, 0, 0, 0
        cosThetaStar, cosTheta1, phi1 = -2., -2., -4.

        for t in self.SingleMuonTriggers:
            if hasattr(event, t) and getattr(event, t): isSingleMuonTrigger = True
        for t in self.SingleMuonPhotonTriggers:
            if hasattr(event, t) and getattr(event, t): isSingleMuonPhotonTrigger = True
        for t in self.SingleMuonNoFiltersPhotonTriggers:
            if hasattr(event, t) and getattr(event, t): isSingleMuonNoFiltersPhotonTrigger = True
        for t in self.DoubleMuonTriggers:
            if hasattr(event, t) and getattr(event, t): isDoubleMuonTrigger = True
        for t in self.DoubleMuonPhotonTriggers:
            if hasattr(event, t) and getattr(event, t): isDoubleMuonPhotonTrigger = True
        for t in self.JPsiTriggers:
            if hasattr(event, t) and getattr(event, t): isJPsiTrigger = True
        for t in self.DisplacedTriggers:
            if hasattr(event, t) and getattr(event, t): isDisplacedTrigger = True
        
        lheWeight = 1.
        
        if self.isMC: 
            # Event weight
            if not self.isLO and hasattr(event, "LHEWeight_originalXWGTUP"): lheWeight = event.LHEWeight_originalXWGTUP
            
            # PU weight
            puWeight = self.puTool.getWeight(event.Pileup_nTrueInt)
        
        self.hists["Nevents"].Fill(0, lheWeight)
        self.hists["Acceptance"].Fill(0, lheWeight)
        self.hists["Cutflow"].Fill(0, lheWeight)
        

        # Gen studies
        if self.isMC and self.isSignal:
            genHIdx, genJPsiIdx, genMuon1Idx, genMuon2Idx, genPhotonIdx = -1, -1, -1, -1, -1
#            print "-"*40
            for i in range(event.nGenPart):
#                print i, "\t", event.GenPart_pdgId[i], "\t", event.GenPart_status[i], "\t", event.GenPart_statusFlags[i], "\t", event.GenPart_pt[i]
                if event.GenPart_pdgId[i] == 25 or event.GenPart_pdgId[i] == 23: genHIdx = i
                if event.GenPart_pdgId[i] == 443: genJPsiIdx = i
                if event.GenPart_pdgId[i] == 22 and event.GenPart_status[i] in [1, 23] and (genPhotonIdx < 0 or event.GenPart_pt[i] > event.GenPart_pt[genPhotonIdx]): genPhotonIdx = i
                if event.GenPart_pdgId[i] == -13 and event.GenPart_status[i] == 1 and (genMuon1Idx < 0 or event.GenPart_pt[i] > event.GenPart_pt[genMuon1Idx]): genMuon1Idx = i
                if event.GenPart_pdgId[i] == +13 and event.GenPart_status[i] == 1 and (genMuon2Idx < 0 or event.GenPart_pt[i] > event.GenPart_pt[genMuon2Idx]): genMuon2Idx = i
            
            if genHIdx >= 0 and genJPsiIdx >= 0 and genPhotonIdx >= 0 and genMuon1Idx >= 0 and genMuon2Idx >= 0:
                genH, genJPsi, genMuon1, genMuon2, genPhoton = TLorentzVector(), TLorentzVector(), TLorentzVector(), TLorentzVector(), TLorentzVector()
                if genHIdx >= 0: genH.SetPtEtaPhiM(event.GenPart_pt[genHIdx], event.GenPart_eta[genHIdx], event.GenPart_phi[genHIdx], event.GenPart_mass[genHIdx])
                if genJPsiIdx >= 0: genJPsi.SetPtEtaPhiM(event.GenPart_pt[genJPsiIdx], event.GenPart_eta[genJPsiIdx], event.GenPart_phi[genJPsiIdx], event.GenPart_mass[genJPsiIdx])
                if genPhotonIdx >= 0: genPhoton.SetPtEtaPhiM(event.GenPart_pt[genPhotonIdx], event.GenPart_eta[genPhotonIdx], event.GenPart_phi[genPhotonIdx], event.GenPart_mass[genPhotonIdx])
                if genMuon1Idx >= 0: genMuon1.SetPtEtaPhiM(event.GenPart_pt[genMuon1Idx], event.GenPart_eta[genMuon1Idx], event.GenPart_phi[genMuon1Idx], event.GenPart_mass[genMuon1Idx])
                if genMuon2Idx >= 0: genMuon2.SetPtEtaPhiM(event.GenPart_pt[genMuon2Idx], event.GenPart_eta[genMuon2Idx], event.GenPart_phi[genMuon2Idx], event.GenPart_mass[genMuon2Idx])
                
    #            if genH.M() > 0. and genJPsi.M() > 0. and genPhoton.Pt() > 0. and genMuon1.M() > 0. and genMuon2.M() > 0.:
                self.hists["genH_pt"].Fill(genH.Pt(), lheWeight)
                self.hists["genH_eta"].Fill(genH.Eta(), lheWeight)
                self.hists["genJPsi_pt"].Fill(genJPsi.Pt(), lheWeight)
                self.hists["genJPsi_eta"].Fill(genJPsi.Eta(), lheWeight)
                self.hists["genPhoton_pt"].Fill(genPhoton.Pt(), lheWeight)
                self.hists["genPhoton_eta"].Fill(genPhoton.Eta(), lheWeight)
                self.hists["genMuon1_pt"].Fill(max(genMuon1.Pt(), genMuon2.Pt()), lheWeight)
                self.hists["genMuon1_eta"].Fill(genMuon1.Eta(), lheWeight)
                self.hists["genMuon2_pt"].Fill(min(genMuon1.Pt(), genMuon2.Pt()), lheWeight)
                self.hists["genMuon2_eta"].Fill(genMuon2.Eta(), lheWeight)
                
                self.hists["genCosThetaStar"].Fill(self.returnCosThetaStar(genH, genJPsi), lheWeight)
                self.hists["genCosTheta1"].Fill(self.returnCosTheta1(genJPsi, genMuon1, genMuon2, genPhoton), lheWeight)
                self.hists["genPhi1"].Fill(self.returnPhi1(genH, genMuon1, genMuon2), lheWeight)
    
                # Acceptance
                if abs(genPhoton.Eta()) < 2.5:
                    self.hists["Acceptance"].Fill(1, lheWeight)
                    if abs(genMuon1.Eta()) < 2.4:
                        self.hists["Acceptance"].Fill(2, lheWeight)
                        if abs(genMuon2.Eta()) < 2.4:
                            self.hists["Acceptance"].Fill(3, lheWeight)
                            self.hists["Cutflow"].Fill(1, lheWeight)
                            if genPhoton.Pt() > 15. and genMuon1.Pt() > 10. and genMuon2.Pt() > 5.:
                                self.hists["Acceptance"].Fill(4, lheWeight)

        # Muons
        m1, m2 = -1, -1
        for i in range(event.nMuon):
            if event.Muon_pt[i] > self.thMuons[0 if m1 < 0 else 1] and abs(event.Muon_eta[i]) < 2.4 and event.Muon_looseId[i]:
                if m1 < 0: m1 = i
                if m2 < 0 and m1 >= 0 and event.Muon_charge[m1] != event.Muon_charge[i]: m2 = i
            
        if m1 < 0 or m2 < 0:
            if self.verbose >= 2: print "- No OS loose muons in acceptance"
            return False
            
        self.hists["Cutflow"].Fill(2, lheWeight)
        
        muon1, muon2 = TLorentzVector(), TLorentzVector()
        muon1.SetPtEtaPhiM(event.Muon_pt[m1], event.Muon_eta[m1], event.Muon_phi[m1], event.Muon_mass[m1])
        muon2.SetPtEtaPhiM(event.Muon_pt[m2], event.Muon_eta[m2], event.Muon_phi[m2], event.Muon_mass[m2])
        muon1v2, muon2v2 = TVector2(muon1.Px(), muon1.Py()), TVector2(muon2.Px(), muon2.Py())
        
        jpsi = muon1 + muon2
        
        if jpsi.M() < 2. or jpsi.M() > 12.:
            if self.verbose >= 2: print "- Dimuon invariant mass < 2 or > 12 GeV"
            return False
        
        self.hists["Cutflow"].Fill(3, lheWeight)
        
        # Photons
        p0 = -1
        for i in range(event.nPhoton):
            if event.Photon_pt[i] > self.thPhoton[0] and abs(event.Photon_eta[i]) < 2.5 and event.Photon_pfRelIso03_all[i] < 0.25: # and event.Photon_mvaID_WP80[i]:
                if p0 < 0: p0 = i
        
        if p0 < 0:
            if self.verbose >= 2: print "- No isolated photons in acceptance"
            return False
        
        self.hists["Cutflow"].Fill(4, lheWeight)
        
        photon = TLorentzVector()
        photon.SetPtEtaPhiM(event.Photon_pt[p0], event.Photon_eta[p0], event.Photon_phi[p0], event.Photon_mass[p0])
        photonv2 = TVector2(photon.Px(), photon.Py())
        
        met, metPlusPhoton = TVector2(), TVector2()
        met.SetMagPhi(event.MET_pt, event.MET_phi)
        metPlusPhoton.Set(met.Px() + photon.Px(), met.Py() + photon.Py())
        
        h = jpsi + photon

        jpsi_pt = jpsi.Pt()
        jpsi_eta = jpsi.Eta()
        jpsi_phi = jpsi.Phi()
        jpsi_mass = jpsi.M()
        jpsi_dEta = abs(muon1.Eta() - muon2.Eta())
        jpsi_dPhi = abs(muon1.DeltaPhi(muon2))
        jpsi_dR = muon1.DeltaR(muon2)
        
        h_pt = h.Pt()
        h_eta = h.Eta()
        h_phi = h.Phi()
        h_mass = h.M()
        h_dEta = abs(jpsi.Eta() - photon.Eta())
        h_dPhi = abs(jpsi.DeltaPhi(photon))
        h_dR = jpsi.DeltaR(photon)
        
        minMuonIso = min(event.Muon_pfRelIso03_all[m1], event.Muon_pfRelIso03_all[m2])
        maxMuonIso = max(event.Muon_pfRelIso03_all[m1], event.Muon_pfRelIso03_all[m2])
        minMuonMetDPhi = min(abs(muon1v2.DeltaPhi(met)), abs(muon2v2.DeltaPhi(met)))
        maxMuonMetDPhi = max(abs(muon1v2.DeltaPhi(met)), abs(muon2v2.DeltaPhi(met)))
        photonMetDPhi = abs(photonv2.DeltaPhi(met))
        metPlusPhotonDPhi = abs(met.DeltaPhi(metPlusPhoton))
        
        cosThetaStar = self.returnCosThetaStar(h, jpsi)
        cosTheta1 = self.returnCosTheta1(jpsi, muon1, muon2, photon)
        phi1 = self.returnPhi1(h, muon1, muon2)

        # Weights
#        if self.isMC:
#            triggerWeight = self.muSFs.getTriggerSF(event.Muon_pt[m1], event.Muon_eta[m1])
#            IdSF1 = self.muSFs.getIdSF(event.Muon_pt[0], event.Muon_eta[0], 2)
#            IsoSF1 = self.muSFs.getIsoSF(event.Muon_pt[0], event.Muon_eta[0])
#            IdSF2 = self.muSFs.getIdSF(event.Muon_pt[1], event.Muon_eta[1], 2)
#            IsoSF2 = self.muSFs.getIsoSF(event.Muon_pt[1], event.Muon_eta[1])
#            IdIsoSF3 = self.elSFs.getIdIsoSF(event.Electron_pt[0], event.Electron_eta[0])
#            leptonWeight = IdSF1 * IsoSF1 * IdSF2 * IsoSF2 * IdIsoSF3
        
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
        
        
        
        ### Event variables ###
        
        # Muons
        for i in range(event.nMuon):
            if i != m1 and i != m2 and event.Muon_pt[i] > 10. and abs(event.Muon_eta[i]) < 2.4 and event.Muon_looseId[i] and event.Muon_pfRelIso03_all[i] < 0.15:
                nCleanMuon += 1
        
        # Electrons
        for i in range(event.nElectron):
            if event.Electron_pt[i] > 10. and abs(event.Electron_eta[i]) < 2.5 and event.Electron_cutBased[i] >= 2:
                nCleanElectron += 1
        
        # Taus
        for i in range(event.nTau):
            if event.Tau_pt[i] > 20. and abs(event.Tau_eta[i]) < 2.5 and event.Tau_idDeepTau2017v2p1VSe[i] >= 16 and event.Tau_idDeepTau2017v2p1VSmu[i] >= 8 and event.Tau_idDeepTau2017v2p1VSjet[i] >= 16 and event.Tau_rawIsodR03[i] < 0.15:
                nCleanTau += 1
        
        # Photons
        for i in range(event.nPhoton):
            if i != p0 and event.Photon_pt[i] > 15. and abs(event.Photon_eta[i]) < 2.5 and event.Photon_pfRelIso03_all[i] < 0.15 and event.Photon_mvaID_WP90[i]:
                nCleanPhoton += 1
        
        # Jets and Event variables
        for i in range(event.nJet):
            if event.Jet_jetId[i] >= 6 and abs(event.Jet_eta[i]) < 2.5:
                HT30 += event.Jet_pt[i]
                nCleanJet += 1
                if event.Jet_btagDeepB[i] >= self.btagMedium: nCleanBTagJet += 1
        
        
        if self.isMC: eventWeightLumi = self.lumiWeight * lheWeight * puWeight * topWeight * qcdnloWeight * qcdnnloWeight * ewknloWeight * triggerWeight * leptonWeight
        
        self.out.fillBranch("isMC", self.isMC)
        self.out.fillBranch("is2016", (self.year == 2016))
        self.out.fillBranch("is2017", (self.year == 2017))
        self.out.fillBranch("is2018", (self.year == 2018))
        self.out.fillBranch("isSingleMuonTrigger", isSingleMuonTrigger)
        self.out.fillBranch("isSingleMuonPhotonTrigger", isSingleMuonPhotonTrigger)
        self.out.fillBranch("isSingleMuonNoFiltersPhotonTrigger", isSingleMuonNoFiltersPhotonTrigger)
        self.out.fillBranch("isDoubleMuonTrigger", isDoubleMuonTrigger)
        self.out.fillBranch("isDoubleMuonPhotonTrigger", isDoubleMuonPhotonTrigger)
        self.out.fillBranch("isJPsiTrigger", isJPsiTrigger)
        self.out.fillBranch("passedMETFilters", passedMETFilters)
        self.out.fillBranch("nCleanElectron", nCleanElectron)
        self.out.fillBranch("nCleanMuon", nCleanMuon)
        self.out.fillBranch("nCleanTau", nCleanTau)
        self.out.fillBranch("nCleanPhoton", nCleanPhoton)
        self.out.fillBranch("nCleanJet", nCleanJet)
        self.out.fillBranch("nCleanBTagJet", nCleanBTagJet)
        self.out.fillBranch("HT30", HT30)
        self.out.fillBranch("iPhoton", p0)
        self.out.fillBranch("iMuon1", m1)
        self.out.fillBranch("iMuon2", m2)
        self.out.fillBranch("JPsi_pt", jpsi_pt)
        self.out.fillBranch("JPsi_eta", jpsi_eta)
        self.out.fillBranch("JPsi_phi", jpsi_phi)
        self.out.fillBranch("JPsi_mass", jpsi_mass)
        self.out.fillBranch("JPsi_dEta", jpsi_dEta)
        self.out.fillBranch("JPsi_dPhi", jpsi_dPhi)
        self.out.fillBranch("JPsi_dR", jpsi_dR)
        self.out.fillBranch("H_pt", h_pt)
        self.out.fillBranch("H_eta", h_eta)
        self.out.fillBranch("H_phi", h_phi)
        self.out.fillBranch("H_mass", h_mass)
        self.out.fillBranch("H_dEta", h_dEta)
        self.out.fillBranch("H_dPhi", h_dPhi)
        self.out.fillBranch("H_dR", h_dR)
        self.out.fillBranch("minMuonIso", minMuonIso)
        self.out.fillBranch("maxMuonIso", maxMuonIso)
        self.out.fillBranch("minMuonMetDPhi", minMuonMetDPhi)
        self.out.fillBranch("maxMuonMetDPhi", maxMuonMetDPhi)
        self.out.fillBranch("photonMetDPhi", photonMetDPhi)
        self.out.fillBranch("metPlusPhotonDPhi", metPlusPhotonDPhi)
        self.out.fillBranch("cosThetaStar", cosThetaStar)
        self.out.fillBranch("cosTheta1", cosTheta1)
        self.out.fillBranch("phi1", phi1)
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
        
        if self.verbose >= 2: print "+ Tree filled"
        
        return True





    def returnCosThetaStar(self, theH, theJPsi):
        h, j = TLorentzVector(theH), TLorentzVector(theJPsi)
        # Boost the Z to the A rest frame
        j.Boost( -h.BoostVector() )
        value = j.CosTheta()
        if value != value or math.isinf(value): return -2.
        return value

    def returnCosTheta1(self, theJPsi, theL1, theL2, thePhoton):
        j, l1, l2, g = TLorentzVector(theJPsi), TLorentzVector(theL1), TLorentzVector(theL2), TLorentzVector(thePhoton)
        # Boost objects to the JPsi rest frame
        l1.Boost( -j.BoostVector() )
        l2.Boost( -j.BoostVector() )
        g.Boost( -j.BoostVector() )
        # cos theta = Gamma dot L1 / (|Gamma|*|L1|)
        value = g.Vect().Dot( l1.Vect() ) / ( (g.Vect().Mag())*(l1.Vect().Mag()) ) if g.Vect().Mag() > 0. and l1.Vect().Mag() > 0. else -2
        if value != value or math.isinf(value): return -2.
        return value


#  TLorentzVector pA(theV);
#  TLorentzVector pL1(theL1);
#  TLorentzVector pL2(theL2);
#  TLorentzVector pB1(theB1);
#  TLorentzVector pB2(theB2);
#  // Boost objects to the A rest frame
#  pL1.Boost( -pA.BoostVector() );
#  pL2.Boost( -pA.BoostVector() );
#  pB1.Boost( -pA.BoostVector() );
#  pB2.Boost( -pA.BoostVector() );
#  // Reconstruct H in A rest frame
#  TLorentzVector pHr = pB1 + pB2;
#  // cos theta = H dot L1 / (|H|*|L1|)
#  float value=pHr.Vect().Dot( pL1.Vect() ) / ( pHr.Vect().Mag()*pL1.Vect().Mag() );
#  if(value!=value || isinf(value)) return -2.;
#  return value;


    def returnPhi1(self, theH, theL1, theL2):
        h, l1, l2 = TLorentzVector(theH), TLorentzVector(theL1), TLorentzVector(theL2)
        beamAxis = TVector3(0., 0., 1.)
        # Boost objects to the A rest frame
        l1.Boost( -h.BoostVector() )
        l2.Boost( -h.BoostVector() )
        # Reconstruct JPsi in H rest frame
        j = l1 + l2
        # Build unit vectors orthogonal to the decay planes
        Zplane = TVector3(l1.Vect().Cross( l2.Vect() )) # L1 x L2
        Bplane = TVector3(beamAxis.Cross( j.Vect() )) # Beam x JPsi, beam/JPsi plane
        if Zplane.Mag() == 0. or Bplane.Mag() == 0.: return -4.
        Zplane.SetMag(1.)
        Bplane.SetMag(1.)
        # Sign of Phi1
        sgn = j.Vect().Dot( Zplane.Cross(Bplane) )
        sgn /= abs(sgn)
        if abs(Zplane.Dot(Bplane)) > 1.: return -5.
        value = sgn * math.acos( Zplane.Dot(Bplane) )
        if value != value or math.isinf(value): return -5.
        return value


