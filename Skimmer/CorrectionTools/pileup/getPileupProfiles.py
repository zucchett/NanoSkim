#! /usr/bin/env python
# Author: Izaak Neutelings (January 2019)
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2017Analysis
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2018Analysis
# https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#PileupInformation

import os, sys, shutil
from argparse import ArgumentParser
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import TFile, TTree

argv = sys.argv
description = '''This script makes pileup profiles for MC and data.'''
parser = ArgumentParser(prog="pileup",description=description,epilog="Succes!")
parser.add_argument('-y', '--year',     dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                        help="select year" )
parser.add_argument('-c', '--channel',  dest='channel', choices=['ll'], type=str, default='ll', action='store',
                                        help="select channel" )
parser.add_argument('-t', '--type',     dest='types', choices=['data','mc'], type=str, nargs='+', default=['data','mc'], action='store',
                                        help="make profile for data and/or MC" )
parser.add_argument('-v', '--verbose',  dest='verbose', default=False, action='store_true', 
                                        help="print verbose" )
args = parser.parse_args()



def getMCProfile(outfilename,indir,samples,channel,year):
    """Get pileup profile in MC by adding Pileup_nTrueInt histograms from a given list of samples."""
    print ">>> getMCProfile(%s)"%(outfilename)
    nprofiles = 0
    histname  = 'pileup'
    tothist   = None    
    for subdir, samplename in samples:
      filename = "%s/%s/%s.root"%(indir,subdir,samplename)
      print ">>>   %s"%(filename)
      file = TFile(filename,'READ')
      if not file or file.IsZombie():
        print ">>>   Warning! getMCProfile: Could not open %s"%(filename)
        continue
      hist      = file.Get(histname)
      if not hist:
        print ">>>   Warning! getMCProfile: Could not open histogram in %s"%(filename)      
        continue
      if tothist==None:
        tothist = hist.Clone('pileup')
        tothist.SetTitle('pileup')
        tothist.SetDirectory(0)
        nprofiles += 1
      else:
        tothist.Add(hist)
        nprofiles += 1
      file.Close()
    print ">>>   added %d MC profiles, %d entries, %.1f mean"%(nprofiles,tothist.GetEntries(),tothist.GetMean())
    
    file = TFile(outfilename,'RECREATE')
    tothist.Write('pileup')
    file.Close()
    


def getDataProfile(outfilename,JSON,pileup,bins,minbias,local=False):
    """Get pileup profile in data with pileupCalc.py tool."""
    print ">>> getDataProfile(%s,%d,%s)"%(outfilename,bins,minbias)
    if local:
      JSON   = copyToLocal(JSON)
      pileup = copyToLocal(pileup)
      command = "./pileupCalc.py -i %s --inputLumiJSON %s --calcMode true --maxPileupBin %d --numPileupBins %d --minBiasXsec %d %s --verbose"%(JSON,pileup,bins,bins,minbias*1000,outfilename)
    else:
      command = "pileupCalc.py -i %s --inputLumiJSON %s --calcMode true --maxPileupBin %d --numPileupBins %d --minBiasXsec %d %s"%(JSON,pileup,bins,bins,minbias*1000,outfilename)
    print ">>>   executing command (this may take a while):"
    print ">>>   " + command
    os.system(command)
    
    # CHECK
    if not os.path.isfile(outfilename):
      print ">>>   Warning! getDataProfile: Could find output file %s!"%(outfilename)
      return    
    file = TFile(outfilename,'READ')
    if not file or file.IsZombie():
      print ">>>   Warning! getDataProfile: Could not open output file %s!"%(outfilename)
      return
    hist = file.Get('pileup')
    print ">>>   pileup profile in data with min. bias %s mb has a mean of %.1f"%(minbias,hist.GetMean())
    file.Close()
    

def copyToLocal(filename):
  """Copy file to current directory, and return new name."""
  fileold = filename
  filenew = filename.split('/')[-1]
  shutil.copyfile(fileold,filenew)
  if not os.path.isfile(filenew):
    print ">>> ERROR! Copy %s failed!"%(filenew)
  return filenew



def main():
    
    years   = args.years
    channel = args.channel
    types   = args.types
    
    for year in args.years:
        filename  = "MC_PileUp_%d.root"%(year)
        indir     = "/work/pbaertsc/heavy_resonance/%d"%(year)
        if year==2016:
            #JSON    = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt"
            JSON    = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt"
            pileup  = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt"  
            samples = [
          ('DY', "DYJetsToLL_HT-100to200"),
          ('DY', "DYJetsToLL_HT-200to400"),
          ('DY', "DYJetsToLL_HT-400to600"),
          ('DY', "DYJetsToLL_HT-600to800"),
          ('DY', "DYJetsToLL_HT-800to1200"),
          ('DY', "DYJetsToLL_HT-1200to2500"),
          ('DY', "DYJetsToLL_HT-2500toInf"),
          ('ZJ', "ZJetsToNuNu_HT-100to200"),
          ('ZJ', "ZJetsToNuNu_HT-200to400"),
          ('ZJ', "ZJetsToNuNu_HT-400to600"),
          ('ZJ', "ZJetsToNuNu_HT-600to800"),
          ('ZJ', "ZJetsToNuNu_HT-800to1200"),
          ('ZJ', "ZJetsToNuNu_HT-1200to2500"),
          ('ZJ', "ZJetsToNuNu_HT-2500toInf"),
          ('WJ', "WJetsToLNu_HT-100to200"),
          ('WJ', "WJetsToLNu_HT-200to400"),
          ('WJ', "WJetsToLNu_HT-400to600"),
          ('WJ', "WJetsToLNu_HT-600to800"),
          ('WJ', "WJetsToLNu_HT-800to1200"),
          ('WJ', "WJetsToLNu_HT-1200to2500"),
          ('WJ', "WJetsToLNu_HT-2500toInf"),
          ('ST', "ST_s-channel"),
          ('ST', "ST_t-channel_top"),
          ('ST', "ST_t-channel_antitop"),
          ('ST', "ST_tW_top"),
          ('ST', "ST_tW_antitop"),
          ('TT', "TTTo2L2Nu"),
          ('TT', "TTToSemiLeptonic"),
          ('TT', "TTWJetsToLNu"),
          ('TT', "TTZToLLNuNu"),     
          ('VV', "WWTo1L1Nu2Q"),
          ('VV', "WWTo2L2Nu"),
          ('VV', "WWTo4Q"),
          ('VV', "WZTo1L1Nu2Q"),
          ('VV', "WZTo2L2Q"),
          ('VV', "ZZTo2L2Q"),
          ('VV', "ZZTo2Q2Nu"),
          ('VV', "ZZTo2L2Nu_ext1"),
          ('VV', "ZZTo2L2Nu_main"),
          ('VV', "ZZTo4L_ext1"),
          ('VV', "ZZTo4L_main"),
          ('VV', "GluGluHToBB"),
          ('VV', "ZH_HToBB_ZToNuNu"),
          ('VV', "ZH_HToBB_ZToLL"),
          ('VV', "WplusH_HToBB_WToLNu"),
          ('VV', "WminusH_HToBB_WToLNu"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M600"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M800"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M1000"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M1200"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M1400"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M1600"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M1800"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M2000"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M2500"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M3000"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M3500"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M4000"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M4500"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M5000"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M5500"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M6000"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M7000"),
          ('XZH',"ZprimeToZHToZlepHinc_narrow_M8000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M600" ),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M800" ),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1200"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1400"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1600"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1800"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M2000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M2500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M3000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M3500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M4000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M4500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M5000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M5500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M6000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M7000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M8000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1200"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1400"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-2000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-2500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-3000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-3500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-4000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-4500"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-5000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-5500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-6000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-7000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-8000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-600" ),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1200"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1400"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-2000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-2500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-3000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-3500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-4000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-4500"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-5000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-5500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-6000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-7000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-8000")
                ]
        elif year==2017:
            JSON    = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt"
            pileup  = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/pileup_latest.txt"    
            samples = [
          ('DY',             "DYJetsToLL_HT-100to200"  ),
          ('DY',             "DYJetsToLL_HT-200to400"  ),
          ('DY',             "DYJetsToLL_HT-400to600"  ),
          ('DY',             "DYJetsToLL_HT-600to800"  ),
          ('DY',             "DYJetsToLL_HT-800to1200" ),
          ('DY',             "DYJetsToLL_HT-1200to2500" ),
          ('DY',             "DYJetsToLL_HT-2500toInf"  ),
          ('ZJ',             "ZJetsToNuNu_HT-100to200"  ),
          ('ZJ',             "ZJetsToNuNu_HT-200to400"  ),
          ('ZJ',             "ZJetsToNuNu_HT-400to600"  ),
          ('ZJ',             "ZJetsToNuNu_HT-600to800"  ),
          ('ZJ',             "ZJetsToNuNu_HT-800to1200" ),
          ('ZJ',             "ZJetsToNuNu_HT-1200to2500"),
          ('ZJ',             "ZJetsToNuNu_HT-2500toInf" ),
          ('WJ',             "WJetsToLNu_HT-100to200"   ),
          ('WJ',             "WJetsToLNu_HT-200to400"   ),
          ('WJ',             "WJetsToLNu_HT-400to600"   ),
          ('WJ',             "WJetsToLNu_HT-600to800"   ),
          ('WJ',             "WJetsToLNu_HT-800to1200"  ),
          ('WJ',             "WJetsToLNu_HT-1200to2500" ),
          ('WJ',             "WJetsToLNu_HT-2500toInf"  ),
          ('ST',             "ST_s-channel"             ),
          ('ST',             "ST_t-channel_antitop"     ),
          ('ST',             "ST_t-channel_top"         ),
          ('ST',             "ST_tW_antitop"            ),
          ('ST',             "ST_tW_top"                ),
          ('TT',             "TTTo2L2Nu"                ),
          ('TT',             "TTToSemiLeptonic"         ),
          ('TT',             "TTWJetsToLNu"             ),
          ('TT',             "TTZToLLNuNu"              ),
          ('VV',             "WWTo1L1Nu2Q"              ),
          ('VV',             "WWTo2L2Nu"                ),
          ('VV',             "WWTo4Q"                   ),
          ('VV',             "WZTo1L1Nu2Q"              ),
          ('VV',             "WZTo2L2Q"                 ),
          ('VV',             "ZZTo2L2Q"                 ),
          ('VV',             "ZZTo2Q2Nu"                ),
          ('VV',             "ZZTo2L2Nu"                ),
          ('VV',             "ZZTo4L"                   ),
          ('VV',             "GluGluHToBB"              ),
          ('VV',             "ZH_HToBB_ZToNuNu"         ),
          ('VV',             "ZH_HToBB_ZToLL"           ),
          ('VV',             "WplusH_HToBB_WToLNu"      ),
          ('VV',             "WminusH_HToBB_WToLNu"     ),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M600" ),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M800" ),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1200"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1400"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1600"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1800"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M2000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M2500"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M3000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M3500"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M4000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M4500"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M5000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M5500"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M6000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M7000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M8000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M600" ),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M800" ),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1200"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1400"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1600"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1800"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M2000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M2500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M3000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M3500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M4000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M4500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M5000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M5500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M6000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M7000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M8000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1200"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1400"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-2000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-2500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-3000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-3500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-4000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-4500"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-5000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-5500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-6000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-7000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-8000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-600" ),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-800" ),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1200"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1400"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-2000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-2500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-3000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-3500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-4000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-4500"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-5000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-5500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-6000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-7000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-8000")
          ]

        
        elif year==2018:
            JSON    = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt"
            pileup  = "/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/pileup_latest.txt"    
            samples = [
          ('DY',             "DYJetsToLL_HT-100to200"),
          ('DY',             "DYJetsToLL_HT-200to400"),
          ('DY',             "DYJetsToLL_HT-400to600"),
          ('DY',             "DYJetsToLL_HT-600to800"),
          ('DY',             "DYJetsToLL_HT-800to1200"),
          ('DY',             "DYJetsToLL_HT-1200to2500"),
          ('DY',             "DYJetsToLL_HT-2500toInf"),
          ('ZJ',             "ZJetsToNuNu_HT-100to200"),
          ('ZJ',             "ZJetsToNuNu_HT-200to400"),
          ('ZJ',             "ZJetsToNuNu_HT-400to600"),
          ('ZJ',             "ZJetsToNuNu_HT-600to800"),
          ('ZJ',             "ZJetsToNuNu_HT-800to1200"),
          ('ZJ',             "ZJetsToNuNu_HT-1200to2500"),
          ('ZJ',             "ZJetsToNuNu_HT-2500toInf"),
          ('WJ',             "WJetsToLNu_HT-100to200"),
          ('WJ',             "WJetsToLNu_HT-200to400"),
          ('WJ',             "WJetsToLNu_HT-400to600"),
          ('WJ',             "WJetsToLNu_HT-600to800"),
          ('WJ',             "WJetsToLNu_HT-800to1200"),
          ('WJ',             "WJetsToLNu_HT-1200to2500"),
          ('WJ',             "WJetsToLNu_HT-2500toInf"),
          ('ST',             "ST_s-channel"),
          ('ST',             "ST_t-channel_top"),
          ('ST',             "ST_t-channel_antitop"),
          ('ST',             "ST_tW_top"),
          ('ST',             "ST_tW_antitop"),
          ('TT',             "TTTo2L2Nu"),
          ('TT',             "TTToSemiLeptonic"),
          ('TT',             "TTWJetsToLNu"),
          ('TT',             "TTZToLLNuNu"),
          ('VV',             "WWTo2L2Nu"),
          ('VV',             "WWTo4Q"),
          ('VV',             "WWTo1L1Nu2Q"),
          ('VV',             "WZTo2L2Q"),
          ('VV',             "ZZTo2Q2Nu"),
          ('VV',             "ZZTo2L2Q"),
          ('VV',             "ZZTo2L2Nu"),
          ('VV',             "ZZTo4L"),
          ('VV',             "GluGluHToBB"),
          ('VV',             "ZH_HToBB_ZToNuNu"),
          ('VV',             "ZH_HToBB_ZToLL"),
          ('VV',             "WplusH_HToBB_WToLNu"),
          ('VV',             "WminusH_HToBB_WToLNu"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M600"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M800"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1200"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1400"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1600"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M1800"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M2000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M2500"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M3000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M3500"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M4000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M4500"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M5000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M5500"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M6000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M7000"),
          ('XZH',            "ZprimeToZHToZlepHinc_narrow_M8000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M600" ),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M800"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1200"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1400"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1600"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M1800"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M2000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M2500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M3000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M3500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M4000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M4500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M5000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M5500"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M6000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M7000"),
          ('XZH',            "ZprimeToZHToZinvHall_narrow_M8000"), 
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1200"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1400"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-1800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-2000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-2500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-3000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-3500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-4000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-4500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-5000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-5500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-6000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-7000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zlephinc_narrow_M-8000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1200"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1400"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1600"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-1800"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-2000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-2500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-3000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-3500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-4000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-4500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-5000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-5500"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-6000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-7000"),
          ('XZHVBF',        "Zprime_VBF_Zh_Zinvhinc_narrow_M-8000")
                ]
      
        # MC
        if 'mc' in args.types:
            getMCProfile(filename,indir,samples,channel,year)
      
        # DATA
        if 'data' in args.types:
            minbiases = [ 69.2, 80.0, 69.2*1.046, 69.2*0.954 ]
            for minbias in minbiases:
                filename = "Data_PileUp_%d_%s.root"%(year,str(minbias).replace('.','p'))
                getDataProfile(filename,JSON,pileup,100,minbias)
      


if __name__ == '__main__':
    print
    main()
    print ">>> done\n"
    

