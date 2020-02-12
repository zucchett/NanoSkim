#! /usr/bin/env python
# Author: Izaak Neutelings (July 2019)
# Description: Check tau triggers in nanoAOD
# Source:
#   https://github.com/cms-tau-pog/TauTriggerSFs/blob/run2_SFs/python/getTauTriggerSFs.py
#   https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py#L78-L94
#   https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html#TrigObj
import os, sys, yaml #json
import numpy as np
from math import sqrt, pi
from utils import ensureDirectory
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
#from collections import namedtuples
from ROOT import PyConfig, gROOT, gDirectory, gPad, gStyle, TFile, TCanvas, TLegend, TLatex, TH1F
PyConfig.IgnoreCommandLineOptions = True
gROOT.SetBatch(True)
gStyle.SetOptTitle(False)
gStyle.SetOptStat(False) #gStyle.SetOptStat(1110)
#TriggerFilter = namedtuples('TriggerFilter','hltpath filters pt')



# LOAD JSON
def loadTriggersFromJSON(filename,verbose=True):
    """Load JSON file for triggers."""
    print ">>> loadTriggersFromJSON: loading '%s'"%(filename)
    filters         = [ ]
    filterpairs     = [ ]
    filterbits_dict = { }
    triggers        = { }
    ids             = { 11: 'ele', 13: 'mu', 15: 'tau' }
    with open(filename,'r') as file:
      #data = json.load(file)
      data = yaml.safe_load(file)
    for id in ['ele','mu','tau']:
      for filterbit, bit in data['filterbits'][id].iteritems():
        filterbits_dict[filterbit] = bit
        filter = TriggerFilter(id,filterbit,bit=bit)
        filters.append(filter)
    for hltpath, trigdict in data['hltpaths'].iteritems():
      runrange     = trigdict.get('runrange',None)
      hltfilters   = [ ]
      for id in ['ele','mu','tau']:
        if id not in trigdict: continue
        ptcut      = trigdict[id]['pt_min']
        etacut     = trigdict[id].get('etacut',2.5)
        filterbits = trigdict[id]['filterbits']
        filter     = TriggerFilter(id,filterbits,hltpath,ptcut,etacut,runrange)
        filter.setbits(filterbits_dict)
        filters.append(filter)
        hltfilters.append(filter)
      assert len(hltfilters)>0, "Did not find any valid filters for '%s' in %s"%(hltpath,trigdict)
      filterpair   = FilterPair(hltpath,*hltfilters)
      filterpairs.append(filterpair)
    filters.sort(key=lambda f: (f.id,-int(f.name in data['filterbits'][ids[f.id]]),f.bits))
    for datatype in data['hltcombs']:
      triggers[datatype] = { }
      for channel, hltcombs in data['hltcombs'][datatype].iteritems():
        exec "triggers[datatype][channel] = lambda e: e."+' or e.'.join(hltcombs) in locals()
    
    # PRINT
    if verbose:
      for datatype in data['hltcombs']:
        print ">>>   %s trigger requirements:"%datatype
        for channel, hltcombs in data['hltcombs'][datatype].iteritems():
          print ">>> %10s:  "%channel + ' || '.join(hltcombs)
      print ">>>   hlt with pair of filters:"
      for pair in filterpairs:
        print ">>> %s (%s)"%(pair.name,pair.channel)
        print ">>>   %3s leg: %s"%(ids[pair.filter1.id],pair.filter1.name)
        print ">>>   %3s leg: %s"%(ids[pair.filter2.id],pair.filter2.name)
      for id in [11,13,15]:
        print ">>> %s filter bits:"%ids[id]
        for filter in filters:
          if filter.id!=id: continue
          print ">>> %6d: %s"%(filter.bits,filter.name)
    
    return filters, filterpairs, triggers
    


# TRIGGER FILTER PAIR
class FilterPair:
    """Container class for filters of triggers of two objects."""
    
    def __init__(self,hltpath,*filters,**kwargs):
        filter1, filter2 = filters[:2] if len(filters)>=2 else (filters[0],filters[0])
        if filter1.id>filter2.id: filter1, filter2 = filter2, filter1
        self.name     = hltpath
        self.hltpath  = hltpath
        self.filter1  = filter1
        self.filter2  = filter2
        self.runrange = kwargs.get('runrange',None)
        self.channel  = ('etau'  if filter1.id==11 else 'mutau' if filter1.id==13 else
                         'ditau' if filter1.id==15 else None)
        exec ("self.hltfired = lambda e: e."+self.hltpath) in locals()
    
# TRIGGER FILTER
class TriggerFilter:
    """Container class for trigger filter."""
    
    def __init__(self,id,filters,hltpath=[],pt=0,eta=2.5,bit=0,runrange=None):
        ids = ['ele','mu','tau',11,13,15]
        assert id in ids, "Trigger object ID must be in %s"%(ids)
        if isinstance(filters,str): filters = [filters]
        if isinstance(hltpath,str): hltpath = [hltpath]
        if isinstance(id,str):
          id = 11 if 'ele' in id else 13 if 'mu' in id else 15 if 'tau' in id else None
        self.filters    = filters
        self.name       = '_'.join(filters)
        self.hltpaths   = hltpath
        self.runrange   = runrange
        self.id         = id
        self.collection = 'Electron' if id==11 else 'Muon' if id==13 else 'Tau' if id==15 else None
        self.pt         = pt
        self.eta        = eta
        self.bits       = bit
        self.channel    = ('etau' if id==11 else 'mutau' if id==13 else
                           'etau' if any('IsoEle' in f for f in filters) else
                           'mutau' if any('IsoMu' in f for f in filters) else 'ditau')
        if self.hltpaths:
          # function to check if a HLT paths were fired in an event (e)
          exec "self.hltfired = lambda e: e."+' or e.'.join(self.hltpaths) in locals()
        else:
          self.hltfired = lambda e: True
        
    def __repr__(self):
        """Returns string representation of TriggerFilter object."""
        return '<%s("%s",%s) at %s>'%(self.__class__.__name__,self.name,self.bits,hex(id(self)))
        
    def setbits(self,filterbits_dict):
        """Compute bits for all filters with some dictionairy."""
        self.bits = 0
        for filter in self.filters:
          assert filter in filterbits_dict, "Could not find filter '%s' in filterbits_dict = %s"%(filter,filterbits_dict)
          self.bits += filterbits_dict[filter] #.get(filter,0)
        
    def hasbits(self,bits):
        """Check if a given set of bits contain this filter's set of bits,
        using the bitwise 'and' operator '&'."""
        return self.bits & bits == self.bits
    
    def match(self,trigobj,recoobj,dR=0.4):
        #if isinstance(recoobj,'TrigObj'): trigobj, recoobj = recoobj, trigobj
        return trigobj.DeltaR(recoobj)<dR and recoobj.pt>self.pt_min and abs(recoobj).eta<self.eta_max
    

# MODULE
class TauTriggerChecks(Module):
    
    def __init__(self,year=2017,wps=['loose','medium','tight'],datatype='mc'):
        
        assert year in [2016,2017,2018], "Year should be 2016, 2017 or 2018"
        assert datatype in ['mc','data'], "Wrong datatype '%s'! It should be 'mc' or 'data'!"%datatype
        
        jsonfile = "json/tau_triggers_%d.json"%year
        filters, filterpairs, triggers = loadTriggersFromJSON(jsonfile)
        
        # FILTER bits
        self.filters     = filters
        self.triggers    = triggers[datatype]
        self.trigger     = lambda e: self.triggers['etau'](e) or self.triggers['mutau'](e) or self.triggers['ditau'](e)
        self.filterpairs = filterpairs
        self.collections = { 11: 'Electron', 13: 'Muon', 15: 'Tau' }
        
        # TAU ID WP bits
        tauIDWPs = { wp: 2**i for i, wp in enumerate(['vvloose','vloose','loose','medium','tight','vtight','vvtight']) }
        assert all(w in tauIDWPs for w in wps), "Tau ID WP should be in %s"%tauIDWPs.keys()
        tauIDWPs = [(0,'all')]+sorted([(tauIDWPs[w],w) for w in wps])
        self.objectIDWPs = { 11: [(0,'all')], 13: [(0,'all')], 15: tauIDWPs }
        for id in self.objectIDWPs:
          print ">>> %s ID WP bits:"%(self.collections[id].lower())
          for wpbit, wp in self.objectIDWPs[id]:
            print ">>> %6d: %s"%(wpbit,wp)
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        """Create branches in output tree."""
        self.out = wrappedOutputTree
        self.out.branch("trigger_etau",  'O')
        self.out.branch("trigger_mutau", 'O')
        self.out.branch("trigger_ditau", 'O')
        for filter in self.filters:
          for wpbit, wp in self.objectIDWPs[filter.id]:
            wptag = "" if wp=='all' else '_'+wp
            self.out.branch("n%s_%s%s"%(filter.collection,filter.name,wptag), 'I')
        for pair in self.filterpairs:
          for wpbit, wp in self.objectIDWPs[15]:
            wptag = "" if wp=='all' else '_'+wp
            self.out.branch("nPair_%s%s"%(pair.name,wptag), 'I')
        
    def analyze(self, event):
        """Process event, return True (pass, go to next module) or False (fail, go to next event)."""
        
        # TRIGGER
        if not self.trigger(event):
          return False
        ###print "%s %s passed the trigger %s"%('-'*20,event.event,'-'*40)
        
        # TRIGGER OBJECTS
        trigObjects   = { }
        for trigobj in Collection(event,'TrigObj'):
          ###print trigobj, trigobj.filterBits
          if trigobj.id not in [11,13,15]: continue
          if trigobj.id not in trigObjects:
            trigObjects[trigobj.id] = { }
          trigObjects[trigobj.id][trigobj] = [ ]
        
        # PREPARE COUNTERS
        nMatches      = { }
        nPairMatches  = { }
        filterMatches = { f: [ ] for f in self.filters }
        for filter in self.filters:
          nMatches[filter] = { }
          default = -2 # filter's trigger was not fired
          if filter.hltfired(event):
            trigObjExists = False
            if filter.id in trigObjects:
              for trigobj, filters in trigObjects[filter.id].iteritems():
                if filter.hasbits(trigobj.filterBits):
                  filters.append(filter)
                  trigObjExists = True
            if trigObjExists:
              default = 0 # event has trigger object for these filter bits
            else:
              default = -1 # event has no trigger object for these filter bits
          for wpbit, wp in self.objectIDWPs[filter.id]:
            nMatches[filter][wpbit] = default
        for pair in self.filterpairs:
          nPairMatches[pair] = { }
          default = -2 # filter's trigger was not fired
          if pair.hltfired(event):
            if nMatches[pair.filter1][0]<0 or nMatches[pair.filter2][0]<0:
              default = -1 # event has trigger object for these filter bits
            else:
              default = 0 # event has no trigger object for these filter bits
          for wpbit, wp in self.objectIDWPs[15]:
            nPairMatches[pair][wpbit] = default
        
        # MATCH ELECTRONS
        if 11 in trigObjects:
          electrons = Collection(event,'Electron')
          for electron in electrons:
            for trigobj, filters in trigObjects[11].iteritems():
              if electron.DeltaR(trigobj)>0.4: continue
              for filter in filters:
                #if electron.pt<filter.pt: continue
                nMatches[filter][0] += 1
                filterMatches[filter].append((trigobj,electron))
        
        # MATCH MUONS
        if 13 in trigObjects:
          muons = Collection(event,'Muon')
          for muon in muons:
            for trigobj, filters in trigObjects[13].iteritems():
              if muon.DeltaR(trigobj)>0.3: continue
              for filter in filters:
                #if muon.pt<filter.pt: continue
                nMatches[filter][0] += 1
                filterMatches[filter].append((trigobj,muon))
        
        # MATCH TAUS
        if 15 in trigObjects:
          taus = Collection(event,'Tau')
          for tau in taus:
            #dm = tau.decayMode
            #if dm not in [0,1,10]: continue
            for trigobj, filters in trigObjects[15].iteritems():
              if tau.DeltaR(trigobj)>0.4: continue
              for filter in filters:
                #if tau.pt<filter.pt: continue
                filterMatches[filter].append((trigobj,tau))
                for wpbit, wp in self.objectIDWPs[15]: # ascending order
                  if tau.idMVAoldDM2017v2<wpbit: break
                  nMatches[filter][wpbit] += 1
        
        # MATCH PAIRS
        for pair in self.filterpairs:
          if pair.filter1==pair.filter2: # for ditau
            for i, (trigobj1,recoobj1) in enumerate(filterMatches[pair.filter1]):
              for trigobj2, recoobj2 in filterMatches[pair.filter1][i+1:]:
                if trigobj1==trigobj2: continue
                if recoobj1==recoobj2: continue
                #if recoobj1.DeltaR(recoobj2)<0.4: continue
                for wpbit, wp in self.objectIDWPs[15]: # ascending order
                  if recoobj1.idMVAoldDM2017v2<wpbit or recoobj2.idMVAoldDM2017v2<wpbit: break
                  nPairMatches[pair][wpbit] += 1
          else: # for eletau and mutau
            for trigobj1, recoobj1 in filterMatches[pair.filter1]:
              for trigobj2, recoobj2 in filterMatches[pair.filter2]:
                if trigobj1.DeltaR(trigobj2)<0.4: continue
                if recoobj1.DeltaR(recoobj2)<0.4: continue
                for wpbit, wp in self.objectIDWPs[15]: # ascending order
                  if recoobj2.idMVAoldDM2017v2<wpbit: break
                  nPairMatches[pair][wpbit] += 1
        
        # FILL BRANCHES
        self.out.fillBranch("trigger_etau",  self.triggers['etau'](event))
        self.out.fillBranch("trigger_mutau", self.triggers['mutau'](event))
        self.out.fillBranch("trigger_ditau", self.triggers['ditau'](event))
        for filter in self.filters:
          for wpbit, wp in self.objectIDWPs[filter.id]:
            wptag = "" if wp=='all' else '_'+wp
            self.out.fillBranch("n%s_%s%s"%(filter.collection,filter.name,wptag),nMatches[filter][wpbit])
        for pair in self.filterpairs:
          for wpbit, wp in self.objectIDWPs[15]:
            wptag = "" if wp=='all' else '_'+wp
            self.out.fillBranch("nPair_%s%s"%(pair.name,wptag
            ),nPairMatches[pair][wpbit])
        return True
        


def getBits(x):
  """Decompose integer into list of bits (powers of 2)."""
  powers = [ ]
  i = 1
  while i <= x:
    if i & x: powers.append(i)
    i <<= 1
  return powers
  


# POST-PROCESSOR
year      = 2017
maxEvts   = -1 #5000 #int(1e4)
nFiles    = 1
postfix   = '_trigger_%s'%(year)
branchsel = "python/keep_and_drop_taus.txt"
if not os.path.isfile(branchsel): branchsel = None
plot      = True #and False

if year==2017:
  infiles = [
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/67/myNanoProdMc2017_NANO_66.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/68/myNanoProdMc2017_NANO_67.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/69/myNanoProdMc2017_NANO_68.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/70/myNanoProdMc2017_NANO_69.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/71/myNanoProdMc2017_NANO_70.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/72/myNanoProdMc2017_NANO_71.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/73/myNanoProdMc2017_NANO_72.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/74/myNanoProdMc2017_NANO_73.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/75/myNanoProdMc2017_NANO_74.root',
    'root://xrootd-cms.infn.it//store/user/aakhmets/taupog/nanoAOD/DYJetsToLLM50_RunIIFall17MiniAODv2_PU2017RECOSIMstep_13TeV_MINIAOD_madgraph-pythia8_v1/76/myNanoProdMc2017_NANO_75.root',
  ]
else:
  infiles = [
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/77/myNanoProdMc2018_NANO_176.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/78/myNanoProdMc2018_NANO_177.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/79/myNanoProdMc2018_NANO_178.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/80/myNanoProdMc2018_NANO_179.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/81/myNanoProdMc2018_NANO_180.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/82/myNanoProdMc2018_NANO_181.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/83/myNanoProdMc2018_NANO_182.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/84/myNanoProdMc2018_NANO_183.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/85/myNanoProdMc2018_NANO_184.root',
    'root://xrootd-cms.infn.it//store/user/jbechtel/taupog/nanoAOD/DYJetsToLLM50_RunIIAutumn18MiniAOD_102X_13TeV_MINIAOD_madgraph-pythia8_v1/86/myNanoProdMc2018_NANO_185.root',
  ]
infiles = infiles[:nFiles]

print ">>> %-10s = %s"%('year',year)
print ">>> %-10s = %s"%('maxEvts',maxEvts)
print ">>> %-10s = %s"%('nFiles',nFiles)
print ">>> %-10s = '%s'"%('postfix',postfix)
print ">>> %-10s = %s"%('infiles',infiles)
print ">>> %-10s = %s"%('branchsel',branchsel)

#module2run = lambda: TauTriggerChecks(year,trigger)
module = TauTriggerChecks(year)
p = PostProcessor(".", infiles, None, branchsel=branchsel, outputbranchsel=branchsel, noOut=False,
                  modules=[module], provenance=False, postfix=postfix, maxEntries=maxEvts)
p.run()



# PLOT
if plot:
  
  def plotMatches(tree,basebranch,trigger,WPs,plotname,header,ctexts):
      gStyle.SetOptTitle(True)
      hists = [ ]
      for i, wp in enumerate(WPs,1):
        ###canvas    = TCanvas('canvas','canvas',100,100,800,600)
        branch    = basebranch + ("" if 'all' in wp else '_'+wp)
        histname  = "%s_%s"%(trigger,branch)
        histtitle = "all (slimmed)"  if wp=='all' else wp #"%s, %s"%(trigger,wp)
        hist = TH1F(histname,histtitle,8,-2,6)
        hist.GetXaxis().SetTitle(branch)
        hist.GetYaxis().SetTitle("Fraction")
        for ibin in xrange(1,hist.GetXaxis().GetNbins()+1):
          xbin = hist.GetBinLowEdge(ibin)
          if xbin==-2:
            hist.GetXaxis().SetBinLabel(ibin,"HLT not fired")
          elif xbin==-1:
            hist.GetXaxis().SetBinLabel(ibin,"No trig. obj.")
          elif xbin==0:
            hist.GetXaxis().SetBinLabel(ibin,"No match")
          elif xbin==1:
            hist.GetXaxis().SetBinLabel(ibin,"1 match")
          else:
            hist.GetXaxis().SetBinLabel(ibin,"%d matches"%xbin)
        hist.GetXaxis().SetLabelSize(0.074)
        hist.GetYaxis().SetLabelSize(0.046)
        hist.GetXaxis().SetTitleSize(0.046)
        hist.GetYaxis().SetTitleSize(0.052)
        hist.GetXaxis().SetTitleOffset(2.14)
        hist.GetYaxis().SetTitleOffset(0.98)
        hist.GetXaxis().SetLabelOffset(0.009)
        if len(branch)>60:
          hist.GetXaxis().CenterTitle(True)
          hist.GetXaxis().SetTitleOffset(2.65)
          hist.GetXaxis().SetTitleSize(0.038)
        elif len(branch)>40:
          hist.GetXaxis().CenterTitle(True)
          hist.GetXaxis().SetTitleOffset(2.16)
          hist.GetXaxis().SetTitleSize(0.044)
        hist.SetLineWidth(2)
        hist.SetLineColor(i)
        out = tree.Draw("%s >> %s"%(branch,histname),"trigger_%s"%trigger,'gOff')
        if hist.Integral()>0:
          hist.Scale(1./hist.Integral())
        else:
          print "Warning! Histogram '%s' is empty!"%hist.GetName()
        ###hist.Draw('HISTE')
        ###canvas.SaveAs(histname+".png")
        ###canvas.SaveAs(histname+".pdf")
        ###canvas.Close()
        hists.append(hist)
      gStyle.SetOptTitle(False)
      canvas   = TCanvas('canvas','canvas',100,100,800,600)
      canvas.SetMargin(0.10,0.09,0.18,0.03)
      textsize = 0.040
      height   = 1.28*(len(hists)+1)*textsize
      legend   = TLegend(0.63,0.70,0.88,0.70-height)
      legend.SetTextSize(textsize)
      legend.SetBorderSize(0)
      legend.SetFillStyle(0)
      legend.SetFillColor(0)
      legend.SetTextFont(62)
      legend.SetHeader(header)
      legend.SetTextFont(42)
      legend.SetMargin(0.2)
      latex = TLatex()
      latex.SetTextAlign(13)
      latex.SetTextFont(42)
      latex.SetNDC(True)
      hists[0].SetMaximum(1.25*max(h.GetMaximum() for h in hists))
      for hist in hists:
        hist.Draw('HISTSAME')
        legend.AddEntry(hist,hist.GetTitle().capitalize(),'l')
      legend.Draw()
      for i, text in enumerate(ctexts):
        textsize = 0.031 if i>0 else 0.044
        latex.SetTextSize(textsize)
        latex.DrawLatex(0.14,0.95-1.7*i*textsize,text)
      canvas.SaveAs(plotname+".png")
      canvas.SaveAs(plotname+".pdf")
      canvas.Close()
      for hist in hists:
        gDirectory.Delete(hist.GetName())
  
  filename = infiles[0].split('/')[-1].replace(".root",postfix+".root")
  file     = TFile(filename)
  tree     = file.Get('Events')
  outdir   = ensureDirectory('plots')
  WPs      = { id: [w[1] for w in wps] for id, wps in module.objectIDWPs.iteritems() }
  
  # PLOT FILTERS
  for filter in module.filters:
    if not filter.hltpaths: continue
    id       = filter.id
    object   = filter.collection
    trigger  = filter.channel
    header   = "#tau_{h} MVAoldDM2017v2" if id==15 else object
    branch   = "n%s_%s"%(object,filter.name)
    channel  = trigger.replace('mu',"#mu").replace('di',"tau").replace('tau',"#tau_{h}")
    plotname = "%s/%s_%s_comparison_%d"%(outdir,trigger,branch,year)
    ctexts   = ["%s channel, %s trigger-reco object matching"%(channel,"#tau_{h}" if id==15 else object.lower())] +\
               ['|| '+t if i>0 else t for i, t in enumerate(filter.hltpaths)]
    plotMatches(tree,branch,trigger,WPs[id],plotname,header,ctexts)
  
  # PLOT PAIRS
  for pair in module.filterpairs:
    trigger  = pair.channel
    branch   = "nPair_%s"%(pair.name)
    header   = "#tau_{h} MVAoldDM2017v2"
    channel  = trigger.replace('mu',"#mu").replace('di',"tau").replace('tau',"#tau_{h}")
    plotname = "%s/%s_%s_comparison_%d"%(outdir,trigger,branch,year)
    ctexts   = ["%s trigger-reco object matching"%channel,pair.hltpath]
    plotMatches(tree,branch,trigger,WPs[15],plotname,header,ctexts)
  
  file.Close()
