#! /usr/bin/env python

import os, multiprocessing
import copy
import math
from array import array
from ROOT import ROOT, gROOT, gStyle, gRandom, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TF1, TH1F, TH2F, THStack
from ROOT import TGraph, TGraphErrors, TGraphAsymmErrors, TVirtualFitter
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TLine

from samples import sample
from variables import variable
from aliases import alias, aliasNames
from plotUtils import *

########## SETTINGS ##########

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-v", "--variable", action="store", type="string", dest="variable", default="")
parser.add_option("-c", "--cut", action="store", type="string", dest="cut", default="")
parser.add_option("-f", "--filename", action="store", type="string", dest="filename", default="")
parser.add_option("-y", "--year", action="store", type="int", dest="year", default=0)
parser.add_option("-n", "--norm", action="store_true", default=False, dest="norm")
parser.add_option("-a", "--all", action="store_true", default=False, dest="all")
parser.add_option("-b", "--bash", action="store_true", default=False, dest="bash")
parser.add_option("-B", "--blind", action="store_true", default=False, dest="blind")

(options, args) = parser.parse_args()
if options.bash: gROOT.SetBatch(True)

########## SETTINGS ##########

#gROOT.SetBatch(True)
#gROOT.ProcessLine("TSystemDirectory::SetDirectory(0)")
#gROOT.ProcessLine("TH1::AddDirectory(kFALSE);")
gStyle.SetOptStat(0)
#TSystemDirectory.SetDirectory(0)

SIGNAL      = 1 # Signal magnification factor
RATIO       = 4 # 0: No ratio plot; !=0: ratio between the top and bottom pads
NORM        = options.norm
PARALLELIZE = False
BLIND       = options.blind
YEAR        = options.year
LUMI        = {0 : 35867.+41530.+59740., 2016 : 35867., 2017: 41530., 2018 : 59740.,}
FILE        = options.filename if len(options.filename) > 0 else None

########## SAMPLES ##########
data = ["data_obs"]
back = ["Higgs", "WmWm", "WpWp", "VVV", "ZZ", "WZ", "WW", "TTTT", "TTZ", "TTW", "ST", "TTbar", "VGamma", "WJetsToLNu", "DYJetsToLL", "QCD"]
sign = []
########## ######## ##########

def plot(var, cut, norm=False, nm1=False):
    ### Preliminary Operations ###
    treeRead = True if not FILE else False # Read from tree
    channel = cut
    isBlind = BLIND
    showSignal = False if 'SB' in cut or 'TR' in cut else True

    # Determine explicit cut
    if treeRead:
        for k in sorted(alias.keys(), key=len, reverse=True):
            if k in cut: cut = cut.replace(k, alias[k])
    
    # Determine Primary Dataset
    pd = []
    if "iSkim==6" in cut: pd = [x for x in sample['data_obs']['files'] if "SingleElectron" in x or "EGamma" in x]
    else: pd = [x for x in sample['data_obs']['files'] if "SingleMuon" in x]
    
    print "Plotting from", ("tree" if treeRead else "file"), var, "in", channel, "channel with:"
    print "  dataset:", pd
    print "  cut    :", cut
    
    ### Create and fill MC histograms ###
    # Create dict
    file = {}
    
    hist = {}
    cutstring = "(eventWeightLumi*stitchWeight)" + ("*("+cut+")" if len(cut)>0 else "")
    
    ### Create and fill MC histograms ###
    jobs = []
    queue = multiprocessing.Queue()
    for i, s in enumerate(data+back+sign):
        for j, ss in enumerate(sample[s]['files']):
            if s in data and not ss in pd: continue
            if YEAR == 2016 and not ('Run2016' in ss or 'Summer16' in ss): continue
            if YEAR == 2017 and not ('Run2017' in ss or 'Fall17' in ss): continue
            if YEAR == 2018 and not ('Run2018' in ss or 'Autumn18' in ss): continue
            if treeRead: # Project from tree
    #            hist[s] = projectLoop(s, pd, var, cutstring)
                p = multiprocessing.Process(target=parallelProject, args=(queue, s, ss, var, cutstring, ))
                jobs.append(p)
                p.start()
            else: # Histogram written to file
                hist[s] = readhist(FILE, s, var, cut)
    # Wait for all jobs to finish
    for job in jobs:
        h = queue.get()
        if not h.GetOption() in hist: hist[h.GetOption()] = h
        else: hist[h.GetOption()].Add(h)
    for job in jobs:
        job.join()
    
    ### Create Bkg Sum histogram ###
    hist['BkgSum'] = hist['data_obs'].Clone("BkgSum") if 'data_obs' in hist else hist[back[0]].Clone("BkgSum")
    hist['BkgSum'].Reset("MICES")
    hist['BkgSum'].SetFillStyle(3003)
    hist['BkgSum'].SetFillColor(1)
    for i, s in enumerate(back): hist['BkgSum'].Add(hist[s])
    
#    if options.norm:
#        for i, s in enumerate(back + ['BkgSum']): hist[s].Scale(hist[data[0]].Integral()/hist['BkgSum'].Integral())

    # Create data and Bkg sum histograms
    if BLIND or 'SR' in channel:
        hist['data_obs'] = hist['BkgSum'].Clone("data_obs")
        hist['data_obs'].Reset("MICES")
    # Set histogram style
    hist['data_obs'].SetMarkerStyle(20)
    hist['data_obs'].SetMarkerSize(1.25)
    
#    for i, s in enumerate(data+back+sign+['BkgSum']): addOverflow(hist[s], False) # Add overflow
    for i, s in enumerate(sign): hist[s].SetLineWidth(3)
    for i, s in enumerate(sign): sample[s]['plot'] = True
    
    # Create stack
    bkg = THStack("Bkg", ";"+hist['BkgSum'].GetXaxis().GetTitle()+";Events")
    for i, s in enumerate(back): bkg.Add(hist[s])
    
    
    # Legend
    leg = TLegend(0.65, 0.6, 0.95, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    if len(data) > 0:
        leg.AddEntry(hist[data[0]], sample[data[0]]['label'], "pe")
    for i, s in reversed(list(enumerate(['BkgSum']+back))):
        leg.AddEntry(hist[s], sample[s]['label'], "f")
    if showSignal:
        for i, s in enumerate(sign):
            if sample[s]['plot']: leg.AddEntry(hist[s], sample[s]['label'], "fl")
        
    leg.SetY1(0.9-leg.GetNRows()*0.04)
    
    
    # --- Display ---
    c1 = TCanvas("c1", hist.values()[0].GetXaxis().GetTitle(), 800, 800 if RATIO else 600)
    
    if RATIO:
        c1.Divide(1, 2)
        setTopPad(c1.GetPad(1), RATIO)
        setBotPad(c1.GetPad(2), RATIO)
    c1.cd(1)
    c1.GetPad(bool(RATIO)).SetTopMargin(0.06)
    c1.GetPad(bool(RATIO)).SetRightMargin(0.05)
    c1.GetPad(bool(RATIO)).SetTicks(1, 1)
    
    logX, logY = "logx" in hist['BkgSum'].GetZaxis().GetTitle(), "logy" in hist['BkgSum'].GetZaxis().GetTitle()
    if logY: c1.GetPad(bool(RATIO)).SetLogy()
    if logX: c1.GetPad(bool(RATIO)).SetLogx()
        
    # Draw
    bkg.Draw("HIST") # stack
    hist['BkgSum'].Draw("SAME, E2") # sum of bkg
    if not isBlind and len(data) > 0: hist['data_obs'].Draw("SAME, PE") # data
    #data_graph.Draw("SAME, PE")
#    if showSignal:
#        smagn = 1. #if treeRead else 1.e2 #if logY else 1.e2
#        for i, s in enumerate(sign):
#    #        if sample[s]['plot']:
#                hist[s].Scale(smagn)
#                hist[s].Draw("SAME, HIST") # signals Normalized, hist[s].Integral()*sample[s]['weight']
#        #textS = drawText(0.80, 0.9-leg.GetNRows()*0.05 - 0.02, stype+" (x%d)" % smagn, True)
    bkg.GetYaxis().SetTitleOffset(bkg.GetYaxis().GetTitleOffset()*1.075)
    bkg.SetMaximum((5. if logY else 1.25)*max(bkg.GetMaximum(), hist['data_obs'].GetBinContent(hist['data_obs'].GetMaximumBin())+hist['data_obs'].GetBinError(hist['data_obs'].GetMaximumBin())))
    #if bkg.GetMaximum() < max(hist[sign[0]].GetMaximum(), hist[sign[-1]].GetMaximum()): bkg.SetMaximum(max(hist[sign[0]].GetMaximum(), hist[sign[-1]].GetMaximum())*1.25)
    bkg.SetMinimum(max(min(hist['BkgSum'].GetBinContent(hist['BkgSum'].GetMinimumBin()), hist['data_obs'].GetMinimum()), 5.e-1)  if logY else 0.)
    if logY:
        bkg.GetYaxis().SetNoExponent(bkg.GetMaximum() < 1.e4)
        bkg.GetYaxis().SetMoreLogLabels(True)
    
    #if logY: bkg.SetMinimum(1)
    leg.Draw()
    drawCMS(LUMI[YEAR], "Preliminary")
    if channel in aliasNames: drawRegion(aliasNames[channel], False)
    #drawAnalysis(channel)
    
    #if nm1 and not cutValue is None: drawCut(cutValue, bkg.GetMinimum(), bkg.GetMaximum()) #FIXME
    #if len(sign) > 0:
    #    if channel.startswith('X') and len(sign)>0: drawNorm(0.9-0.05*(leg.GetNRows()+1), "#sigma(X) = %.1f pb" % 1.)
    
    setHistStyle(bkg, 1.2 if RATIO else 1.1)
    setHistStyle(hist['BkgSum'], 1.2 if RATIO else 1.1)
       
    if RATIO:
        c1.cd(2)
        if logX: c1.GetPad(2).SetLogx()
        err = hist['BkgSum'].Clone("BkgErr;")
        err.SetTitle("")
        err.GetYaxis().SetTitle("Data / Bkg")
        for i in range(1, err.GetNbinsX()+1):
            err.SetBinContent(i, 1)
            if hist['BkgSum'].GetBinContent(i) > 0:
                err.SetBinError(i, hist['BkgSum'].GetBinError(i)/hist['BkgSum'].GetBinContent(i))
        setBotStyle(err)
        errLine = err.Clone("errLine")
        errLine.SetLineWidth(1)
        errLine.SetFillStyle(0)
        res = hist['data_obs'].Clone("Residues")
        for i in range(0, res.GetNbinsX()+1):
            if hist['BkgSum'].GetBinContent(i) > 0: 
                res.SetBinContent(i, res.GetBinContent(i)/hist['BkgSum'].GetBinContent(i))
                res.SetBinError(i, res.GetBinError(i)/hist['BkgSum'].GetBinContent(i))
        setBotStyle(res)
        #err.GetXaxis().SetLabelOffset(err.GetXaxis().GetLabelOffset()*5)
        #err.GetXaxis().SetTitleOffset(err.GetXaxis().GetTitleOffset()*2)
        err.Draw("E2")
        errLine.Draw("SAME, HIST")
        if not isBlind and len(data) > 0:
            res.Draw("SAME, PE0")
            #res_graph.Draw("SAME, PE0")
            if len(err.GetXaxis().GetBinLabel(1))==0: # Bin labels: not a ordinary plot
                drawRatio(hist['data_obs'], hist['BkgSum'])
                drawStat(hist['data_obs'], hist['BkgSum'])
    
    c1.Update()
    
    if True: #gROOT.IsBatch():
        varname = var.replace('.', '_').replace('()', '')
        if not os.path.exists("plots/"+channel): os.makedirs("plots/"+channel)
        c1.Print("plots/"+channel+"/"+varname+".png")
        c1.Print("plots/"+channel+"/"+varname+".pdf")
    
    # Print table
    printTable(hist, sign)
    
    
    if not gROOT.IsBatch(): raw_input("Press Enter to continue...")

    


def plotAll():
    gROOT.SetBatch(True)
    
    hists = {}
    
    for c, l in hists.iteritems():
        for h in l:
            plot(h, c)



if options.all: plotAll()
#elif options.norm: plotNorm(options.variable, options.cut)
else: plot(options.variable, options.cut)

