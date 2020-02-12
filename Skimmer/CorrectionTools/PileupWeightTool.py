#! /bin/usr/env python
# Author: Izaak Neutelings (November 2018)
from ROOT import TFile
from ScaleFactorTool import ensureTFile

from global_paths import MAINDIR
path = MAINDIR + 'CorrectionTools/pileup/'

class PileupWeightTool:
    
    def __init__( self, year=2017, sigma='central' ):
        """Load data and MC pilup profiles."""
        
        assert( year in [2016,2017,2018] ), "You must choose a year from: 2016, 2017, or 2018."
        assert( sigma in ['central','up','down'] ), "You must choose a s.d. variation from: 'central', 'up', or 'down'."
        
        minbias = '69p2'
        if sigma=='down':
          minbias = '66p0168' # -4.6%
        elif sigma=='up':
          minbias = '72p3832' # +4.6%
        
        if year==2016:
          self.datafile = ensureTFile( path+'Data_PileUp_2016_%s.root'%(minbias), 'READ')
          self.mcfile   = ensureTFile( path+'MC_PileUp_2016.root', 'READ')
        elif year==2017:
          self.datafile = ensureTFile( path+'Data_PileUp_2017_%s.root'%(minbias), 'READ')
          self.mcfile   = ensureTFile( path+'MC_PileUp_2017.root', 'READ')
        else:
          self.datafile = ensureTFile( path+'Data_PileUp_2018_%s.root'%(minbias), 'READ')
          self.mcfile   = ensureTFile( path+'MC_PileUp_2018.root', 'READ')
        self.datahist = self.datafile.Get('pileup')
        self.mchist   = self.mcfile.Get('pileup')
        self.datahist.SetDirectory(0)
        self.mchist.SetDirectory(0)
        self.datahist.Scale(1./self.datahist.Integral())
        self.mchist.Scale(1./self.mchist.Integral())
        self.datafile.Close()
        self.mcfile.Close()
        
    
    def getWeight(self,npu):
        """Get pileup weight for a given number of pileup interactions."""
        data = self.datahist.GetBinContent(self.datahist.GetXaxis().FindBin(npu))
        mc   = self.mchist.GetBinContent(self.mchist.GetXaxis().FindBin(npu))
        if mc>0.:
          return data/mc
        print ">>> Warning! PileupWeightTools.getWeight: Could not make pileup weight for npu=%s data=%s, mc=%s"%(npu,data,mc)  
        return 1.
    
