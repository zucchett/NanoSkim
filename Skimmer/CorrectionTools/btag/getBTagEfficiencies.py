#! /usr/bin/env python
# Author: Izaak Neutelings (January 2019)

import os, sys
from argparse import ArgumentParser
import ROOT; ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gStyle, gROOT, TFile, TTree, TH2F, TCanvas, kRed
gStyle.SetOptStat(False)
gROOT.SetBatch(True)

argv = sys.argv
description = '''This script extracts histograms to create b tag efficiencies.'''
parser = ArgumentParser(prog="pileup",description=description,epilog="Succes!")
parser.add_argument('-y', '--year',    dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
                                       help="year to run" )
parser.add_argument('-t', '--tagger',  dest='taggers', choices=['CSVv2','DeepCSV'], type=str, nargs='+', default=['CSVv2','DeepCSV'], action='store',
                                       help="tagger to run" )
parser.add_argument('-w', '--wp',      dest='wps', choices=['loose','medium','tight'], type=str, nargs='+', default=['loose'], action='store',
                                       help="working point to run" )
parser.add_argument('-p', '--plot',    dest="plot", default=False, action='store_true', 
                                       help="plot efficiencies" )
parser.add_argument('-v', '--verbose', dest="verbose", default=False, action='store_true', 
                                       help="print verbose" )
args = parser.parse_args()



def getBTagEfficiencies(tagger,wp,outfilename,indir,samples,jettype,plot=False):
    """Get pileup profile in MC by adding Pileup_nTrueInt histograms from a given list of samples."""
    print ">>> getBTagEfficiencies(%s)"%(outfilename)
    
    # GET HISTOGRAMS
    nhists  = { }
    hists   = { }
    if jettype == 'AK8':
        if tagger == 'CSVv2':
            histdir = 'AK8btag'
        elif tagger == 'DeepCSV':
            histdir = 'AK8btag_deep'
    elif jettype == 'AK4':
        if tagger == 'CSVv2':
            histdir = 'AK4btag'
        elif tagger == 'DeepCSV':
            histdir = 'AK4btag_deep'
    for flavor in ['b','c','udsg']:
      histname = '%s_%s_%s'%(tagger,flavor,wp)
      hists[histname] = None
      hists[histname+'_all'] = None   
    for subdir, samplename in samples:
      filename = "%s/%s/%s.root"%(indir,subdir,samplename)
      print ">>>   %s"%(filename)
      file = TFile(filename,'READ')
      if not file or file.IsZombie():
        print ">>>   Warning! getBTagEfficiencies: Could not open %s"%(filename)
        continue
      for histname in hists:
        histpath = "%s/%s"%(histdir,histname)
        hist = file.Get(histpath)
        if not hist:
          print ">>>   Warning! getBTagEfficiencies: Could not open histogram '%s' in %s"%(histpath,filename)        
          dir = file.Get(histdir)
          if dir: dir.ls()
          continue
        if hists[histname]==None:
          hists[histname] = hist.Clone(histname)
          hists[histname].SetDirectory(0)
          nhists[histname] = 1
        else:
          hists[histname].Add(hist)
          nhists[histname] += 1
      file.Close()
    if len(nhists)>0:
      print ">>>   added %d MC hists:"%(sum(nhists[n] for n in nhists))
      for histname, nhist in nhists.iteritems():
        print ">>>     %-26s%2d"%(histname+':',nhist)
    else:
      print ">>>   no histograms added !"
      return
    
    # SAVE HISTOGRAMS
    print ">>>   writing to %s..."%(outfilename)
    file = TFile(outfilename,'UPDATE') #RECREATE
    ensureTDirectory(file,'ll')
    for histname, hist in hists.iteritems():
      if 'all' in histname:
        continue
      histname_all = histname+'_all'
      histname_eff = 'eff_'+histname
      print ">>>      writing %s..."%(histname)
      print ">>>      writing %s..."%(histname_all)
      print ">>>      writing %s..."%(histname_eff)
      hist_all = hists[histname_all]
      hist_eff = hist.Clone(histname_eff)
      hist_eff.SetTitle(makeTitle(histname_eff))
      hist_eff.Divide(hist_all)
      hist.Write(histname,TH2F.kOverwrite)
      hist_all.Write(histname_all,TH2F.kOverwrite)
      hist_eff.Write(histname_eff,TH2F.kOverwrite)
      if plot:
        plot2D(histname_eff,hist_eff,log=True)
        plot2D(histname_eff,hist_eff,log=False)
    file.Close()
  

def plot2D(histname,hist,log=False):
    """Plot efficiency."""
    dir    = ensureDirectory('plots')
    name   = "%s/%s"%(dir,histname)
    if log:
      name += "_log"
    xtitle = 'jet p_{T} [GeV]'
    ytitle = 'jet #eta'
    ztitle = 'b tag efficiencies' if '_b_' in histname else 'b miss-tag rate'
    
    canvas = TCanvas('canvas','canvas',100,100,800,700)
    canvas.SetFillColor(0)
    canvas.SetBorderMode(0)
    canvas.SetFrameFillStyle(0)
    canvas.SetFrameBorderMode(0)
    canvas.SetTopMargin(  0.07 ); canvas.SetBottomMargin( 0.13 )
    canvas.SetLeftMargin( 0.12 ); canvas.SetRightMargin(  0.17 )
    canvas.SetTickx(0); canvas.SetTicky(0)
    canvas.SetGrid()
    if log:
      canvas.SetLogz()
    canvas.cd()
    
    hist.Draw('COLZTEXT77')
    hist.GetXaxis().SetTitle(xtitle)
    hist.GetYaxis().SetTitle(ytitle)
    hist.GetZaxis().SetTitle(ztitle)
    hist.GetXaxis().SetLabelSize(0.048)
    hist.GetYaxis().SetLabelSize(0.048)
    hist.GetZaxis().SetLabelSize(0.048)
    hist.GetXaxis().SetTitleSize(0.058)
    hist.GetYaxis().SetTitleSize(0.058)
    hist.GetZaxis().SetTitleSize(0.056)
    hist.GetXaxis().SetTitleOffset(1.03)
    hist.GetYaxis().SetTitleOffset(1.04)
    hist.GetZaxis().SetTitleOffset(1.03)
    hist.GetZaxis().SetLabelOffset(-0.005 if log else 0.005)
    hist.SetMinimum(0.01 if log else 0.0)
    hist.SetMaximum(1.0)
    
    gStyle.SetPaintTextFormat('.2f')
    hist.SetMarkerSize(1.0)
    hist.SetMarkerColor(kRed)
    hist.SetMarkerSize(1)
    
    canvas.SaveAs(name+'.pdf')
    canvas.SaveAs(name+'.png')
    canvas.Close()
  

def makeTitle(string):
  string = string.replace('_',' ')
  string = string.replace(' c ',' c jet ')
  string = string.replace(' udsg ',' light-flavor jet ')
  return string
  

def ensureTDirectory(file,dirname):
  dir = file.GetDirectory(dirname)
  if not dir:
    dir = file.mkdir(dirname)
    print ">>>   created directory %s in %s" % (dirname,file.GetName())
  dir.cd()
  return dir
  

def ensureDirectory(dirname):
  """Make directory if it does not exist."""
  if not os.path.exists(dirname):
    os.makedirs(dirname)
    print '>>> made directory "%s"'%(dirname)
    if not os.path.exists(dirname):
      print '>>> failed to make directory "%s"'%(dirname)
  return dirname
  

def main():
    years    = args.years
    for year in args.years:
        if year==2016:
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
                

        
        for tagger in args.taggers:
            if tagger in ['CSVv2','DeepCSV']:
                for jettype in ['AK8','AK4']:
                    for wp in args.wps:
                        filename = "%s_%s_%d_eff.root"%(tagger,jettype,year)
                        indir    = "/work/pbaertsc/heavy_resonance/%d"%(year)
                        getBTagEfficiencies(tagger,wp,filename,indir,samples,jettype,plot=args.plot)
            else:
                jettype = 'AK8'
                for wp in args.wps:
                    filename = "%s_%s_%d_eff.root"%(tagger,jettype,year)
                    indir    = "/work/pbaertsc/heavy_resonance/%d"%(year)
                    getBTagEfficiencies(tagger,wp,filename,indir,samples,jettype,plot=args.plot)
    


if __name__ == '__main__':
    print
    main()
    print ">>> done\n"
    

