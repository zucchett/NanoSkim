#! /bin/usr/env python
# Author: Izaak Neutelings (January 2019)
# https://twiki.cern.ch/twiki/bin/view/CMS/BTagSFMethods
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/BTagCalibration
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation80XReReco
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
from array import array
from ScaleFactorTool import ensureTFile
import ROOT
#ROOT.gROOT.ProcessLine('.L ./BTagCalibrationStandalone.cpp+')
from ROOT import TH2F, BTagCalibration, BTagCalibrationReader
from ROOT.BTagEntry import OP_LOOSE, OP_MEDIUM, OP_TIGHT, OP_RESHAPING
from ROOT.BTagEntry import FLAV_B, FLAV_C, FLAV_UDSG

from global_paths import MAINDIR
path = MAINDIR + 'CorrectionTools/btag/'

class BTagWPs:
  """Contain b tagging working points."""
  def __init__( self, tagger, year=2017 ):
    assert( year in [2016,2017,2018] ), "You must choose a year from: 2016, 2017, or 2018."
    if year==2016:
      if 'deep' in tagger.lower():
        self.loose    = 0.2217 # 0.2219 for 2016ReReco vs. 2016Legacy
        self.medium   = 0.6321 # 0.6324
        self.tight    = 0.8953 # 0.8958
      else:
        self.loose    = 0.5426 # for 80X ReReco
        self.medium   = 0.8484
        self.tight    = 0.9535
    elif year==2017:
      if 'deep' in tagger.lower():
        self.loose    = 0.1522 # for 94X
        self.medium   = 0.4941
        self.tight    = 0.8001
      else:
        self.loose    = 0.5803 # for 94X
        self.medium   = 0.8838
        self.tight    = 0.9693
    elif year==2018:
      if 'deep' in tagger.lower():
        self.loose    = 0.1241 # for 102X
        self.medium   = 0.4184
        self.tight    = 0.7527
      else:
        self.loose    = 0.5803 # for 94X
        self.medium   = 0.8838
        self.tight    = 0.9693
  

class BTagWeightTool:
    
    def __init__(self, tagger, jettype, wp='loose', sigma='central', channel='ll', year=2017):
        """Load b tag weights from CSV file."""
        #print "Loading BTagWeightTool for %s (%s WP)..."%(tagger,wp)
        
        assert(year in [2016,2017,2018]), "You must choose a year from: 2016, 2017, or 2018."
        assert(tagger in ['CSVv2','DeepCSV']), "BTagWeightTool: You must choose a tagger from: CSVv2, DeepCSV!"
        assert(wp in ['loose','medium','tight']), "BTagWeightTool: You must choose a WP from: loose, medium, tight!"
        assert(sigma in ['central','up','down']), "BTagWeightTool: You must choose a WP from: central, up, down!"
    
        
        # FILE
        if year==2016:
          if jettype=='AK8':
            if tagger == 'CSVv2':
              csvname = path+'CSVv2_Moriond17_B_H.csv'
              effname = path+'CSVv2_AK8_2016_eff.root'
            elif tagger == 'DeepCSV':
              csvname = path+'DeepCSV_2016LegacySF_V1.csv'
              effname = path+'DeepCSV_AK8_2016_eff.root'
          elif jettype=='AK4':
            if tagger == 'CSVv2':
              csvname = path+'CSVv2_Moriond17_B_H.csv'
              effname = path+'CSVv2_AK4_2016_eff.root'
            elif tagger == 'DeepCSV':
              csvname = path+'DeepCSV_2016LegacySF_V1.csv'
              effname = path+'DeepCSV_AK4_2016_eff.root'
        elif year==2017:
          if jettype=='AK8':
            if tagger == 'CSVv2':
              csvname = path+'CSVv2_94XSF_V2_B_F.csv'
              effname = path+'CSVv2_AK8_2017_eff.root'
            elif tagger == 'DeepCSV':
              csvname = path+'DeepCSV_94XSF_V4_B_F.csv'
              effname = path+'DeepCSV_AK8_2017_eff.root' 
          elif jettype=='AK4':
            if tagger == 'CSVv2':
              csvname = path+'CSVv2_94XSF_V2_B_F.csv'
              effname = path+'CSVv2_AK4_2017_eff.root'
            elif tagger == 'DeepCSV':
              csvname = path+'DeepCSV_94XSF_V4_B_F.csv'
              effname = path+'DeepCSV_AK4_2017_eff.root'
        elif year==2018:
          if jettype=='AK8':
            if tagger == 'CSVv2':
              csvname = path+'CSVv2_94XSF_V2_B_F.csv'
              effname = path+'CSVv2_AK8_2018_eff.root'
            elif tagger == 'DeepCSV':
              csvname = path+'DeepCSV_102XSF_V1.csv'
              effname = path+'DeepCSV_AK8_2018_eff.root'
          elif jettype=='AK4':
            if tagger == 'CSVv2':
              csvname = path+'CSVv2_94XSF_V2_B_F.csv'
              effname = path+'CSVv2_AK4_2018_eff.root'
            elif tagger == 'DeepCSV':
              csvname = path+'DeepCSV_102XSF_V1.csv'
              effname = path+'DeepCSV_AK4_2018_eff.root'
        # TAGGING WP
        self.wp     = getattr(BTagWPs(tagger,year),wp)
        if jettype == 'AK4':
          if tagger == 'CSVv2':
            tagged = lambda e,i: e.Jet_btagCSVV2[i]>self.wp
          elif tagger == 'DeepCSV':
            tagged = lambda e,i: e.Jet_btagDeepB[i]>self.wp
        elif jettype == 'AK8':
          if tagger == 'CSVv2':
            tagged = lambda e,i: e.FatJet_btagCSVV2[i]>self.wp
          elif tagger == 'DeepCSV':
            tagged = lambda e,i: e.FatJet_btagDeepB[i]>self.wp
          #elif tagger == 'Hbb':
          #  tagged = lambda e,i: e.FatJet_btagHbb[i]>self.wp
        # CSV READER
        op        = OP_LOOSE if wp=='loose' else OP_MEDIUM if wp=='medium' else OP_TIGHT if wp=='tight' else OP_RESHAPING
        type_udsg = 'incl'
        type_bc   = 'comb' # 'mujets' for QCD; 'comb' for QCD+TT
        calib     = BTagCalibration(tagger, csvname)
        reader    = BTagCalibrationReader(op, sigma)
        reader.load(calib, FLAV_B, type_bc)
        reader.load(calib, FLAV_C, type_bc)
        reader.load(calib, FLAV_UDSG, type_udsg)
    
        # EFFICIENCIES
        ptbins     = array('d',[10,20,30,50,70,100,140,200,300,500,1000,1500])
        etabins    = array('d',[-2.5,-1.5,0.0,1.5,2.5])
        bins       = (len(ptbins)-1,ptbins,len(etabins)-1,etabins)
        hists      = { }
        effs       = { }
        
        if tagger in ['CSVv2','DeepCSV']:
          efffile    = ensureTFile(effname)
          for flavor in [0,4,5]:
            flavor   = flavorToString(flavor)
            histname = "%s_%s_%s"%(tagger,flavor,wp)
            effname  = "%s/eff_%s_%s_%s"%(channel,tagger,flavor,wp)
            hists[flavor]        = TH2F(histname,histname,*bins)
            hists[flavor+'_all'] = TH2F(histname+'_all',histname+'_all',*bins)
            effs[flavor]         = efffile.Get(effname)
            hists[flavor].SetDirectory(0)
            hists[flavor+'_all'].SetDirectory(0)
            effs[flavor].SetDirectory(0)
          efffile.Close()
        else:
          efffile    = ensureTFile(effname)
          for flavor in [0,4,5]:
            flavor   = flavorToString(flavor)
            histname = "%s_%s_%s"%(tagger,flavor,wp)
            effname  = "%s/eff_%s_%s_%s"%(channel,tagger,flavor,wp)
            hists[flavor]        = TH2F(histname,histname,*bins)
            hists[flavor+'_all'] = TH2F(histname+'_all',histname+'_all',*bins)
            #effs[flavor]         = efffile.Get(effname)
            hists[flavor].SetDirectory(0)
            hists[flavor+'_all'].SetDirectory(0)
            #effs[flavor].SetDirectory(0)
          efffile.Close()
        
        self.tagged = tagged
        self.calib  = calib
        self.reader = reader
        self.hists  = hists
        self.effs   = effs

    def getWeight(self,event,jetids):
        """Get event weight for a given set of jets."""
        weight = 1.
        for id in jetids:
          weight *= self.getSF(event.Jet_pt[id],event.Jet_eta[id],event.Jet_partonFlavour[id],self.tagged(event,id))
        return weight

    def getSF(self,pt,eta,flavor,tagged):
        """Get b tag SF for a single jet."""
        FLAV = flavorToFLAV(flavor)
        if   eta>=+2.4: eta = +2.399 # BTagCalibrationReader returns zero if |eta| > 2.4
        elif eta<=-2.4: eta = -2.399
        if pt > 1000.: pt = 999 # BTagCalibrationReader returns zero if pt > 1000
        SF   = self.reader.eval(FLAV,abs(eta),pt) #eval_auto_bounds
        if tagged:
          weight = SF
        else:
          eff = self.getEfficiency(pt,eta,flavor)
          if eff==1:
            print "Warning! BTagWeightTool.getSF: MC efficiency is 1 for pt=%s, eta=%s, flavor=%s, SF=%s"%(pt,eta,flavor,SF)
            return 1
          else:
            weight = (1-SF*eff)/(1-eff)
        return weight

        
    def getEfficiency(self,pt,eta,flavor):
        """Get SF for one jet."""
        flavor = flavorToString(flavor)
        hist   = self.effs[flavor]
        xbin   = hist.GetXaxis().FindBin(pt)
        ybin   = hist.GetYaxis().FindBin(eta)
        if xbin==0: xbin = 1
        elif xbin>hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>hist.GetYaxis().GetNbins(): ybin -= 1
        sf     = hist.GetBinContent(xbin,ybin)
        return sf
        
    def fillEfficiencies(self,event,jetids):
        """Fill efficiency of MC."""
        for id in jetids:
          flavor = flavorToString(event.Jet_partonFlavour[id])
          if self.tagged(event,id):
            self.hists[flavor].Fill(event.Jet_pt[id],event.Jet_eta[id])
          self.hists[flavor+'_all'].Fill(event.Jet_pt[id],event.Jet_eta[id])
        
    def setDirectory(self,directory,subdirname=None):
        if subdirname:
          subdir = directory.Get(subdirname)
          if not subdir:
            subdir = directory.mkdir(subdirname)
          directory = subdir
        for histname, hist in self.hists.iteritems():
          hist.SetDirectory(directory)

def flavorToFLAV(flavor):
  return FLAV_B if abs(flavor)==5 else FLAV_C if abs(flavor)==4 or abs(flavor)==15 else FLAV_UDSG       

def flavorToString(flavor):
  return 'b' if abs(flavor)==5 else 'c' if abs(flavor)==4 else 'udsg'
  

