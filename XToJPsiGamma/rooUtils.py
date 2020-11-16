#! /usr/bin/env python

import os, sys, getopt, multiprocessing
import copy, math, pickle
from array import array
import ROOT
from ROOT import gROOT, gSystem, gStyle, gRandom
from ROOT import TObject, TMath, TFile, TChain, TTree, TCut, TH1F, TH2F, THStack, TF1, TGraph, TGaxis
from ROOT import TStyle, TCanvas, TPad, TLegend, TLatex, TText
from ROOT import RooFit, RooPlot


def setPadStyle(h, r=1.2, isTop=False):
    h.GetXaxis().SetTitleSize(h.GetXaxis().GetTitleSize()*r*r)
    h.GetYaxis().SetTitleSize(h.GetYaxis().GetTitleSize()*r)
    h.GetXaxis().SetLabelSize(h.GetXaxis().GetLabelSize()*r)
    h.GetYaxis().SetLabelSize(h.GetYaxis().GetLabelSize()*r)
    if isTop: h.GetXaxis().SetLabelOffset(0.04)
#    h.GetXaxis().SetTitleOffset(h.GetXaxis().GetTitleOffset()*r)
#    h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset())

def fixData(hist, blindRanges=[], useGarwood=False, cutGrass=False, maxPoisson=False):
    if hist==None: return
    varBins = ((hist.GetX()[1] - hist.GetX()[0]) != (hist.GetX()[hist.GetN()-1] - hist.GetX()[hist.GetN()-2])) #hist.GetXaxis().IsVariableBinSize()
    avgwidth = (hist.GetX()[hist.GetN()-1]+hist.GetErrorXhigh(hist.GetN()-1) - (hist.GetX()[0]-hist.GetErrorXlow(0))) / hist.GetN()
    alpha = 1 - 0.6827

    for i in list(reversed(range(0, hist.GetN()))):
        #print "bin", i, "x:", hist.GetX()[i], "y:", hist.GetY()[i]
        width = hist.GetErrorXlow(i) + hist.GetErrorXhigh(i)
        # X error bars to 0 - do not move this, otherwise the first bin will disappear, thanks Wouter and Rene!
        if not varBins:
            hist.SetPointEXlow(i, 0)
            hist.SetPointEXhigh(i, 0)
        # Garwood confidence intervals
        if(useGarwood):
            N = hist.GetY()[i]
            r = width / avgwidth
            #print i, width, avgwidth, r
            if varBins: N = hist.GetY()[i] / r
            N = max(N, 0.) # Avoid unphysical bins
            L = ROOT.Math.gamma_quantile(alpha/2, N, 1.) if N>0 else 0.
            U = ROOT.Math.gamma_quantile_c(alpha/2, N+1, 1)
            #print i, hist.GetErrorYlow(i), hist.GetErrorYhigh(i), N-L, U-N
            # maximum between Poisson and Sumw2 error bars
            EL = N-L if not maxPoisson else max(N-L, hist.GetErrorYlow(i))
            EU = U-N if not maxPoisson else max(U-N, hist.GetErrorYhigh(i))
            hist.SetPointEYlow(i, EL)
            hist.SetPointEYhigh(i, EU)
        # Cut grass
        if cutGrass and hist.GetY()[i] > 0.: cutGrass = False
        # Treatment for 0 bins
        if abs(hist.GetY()[i])<=1.e-6:
            if cutGrass: hist.SetPointError(i, hist.GetErrorXlow(i), hist.GetErrorXhigh(i), 1.e-6, 1.e-6, )
        for r in blindRanges:
            if (hist.GetX()[i] > r[0] and hist.GetX()[i] < r[1]):
                hist.SetPointError(i, hist.GetErrorXlow(i), hist.GetErrorXhigh(i), 1.e-6, 1.e-6, )
                hist.SetPoint(i, hist.GetX()[i], -1.e-4)

        # X error bars
        #if hist.GetErrorXlow(i)<1.e-4:
        #    binwidth = hist.GetX()[1]-hist.GetX()[0]
        #    hist.SetPointEXlow(i, binwidth/2.)
        #    hist.SetPointEXhigh(i, binwidth/2.)


def likelihoodScan(model, dataset, par = []):

    nll = model.createNLL(dataset, RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.SumW2Error(False)) #RooFit.NumCPU(10)

    #gROOT.SetBatch(False)
    nv = (len(par)-1) / 2 + 1
    nh = len(par) / 2 + 1

    c_scan = TCanvas("c_scan", "Likelihood scan", 800*nh, 600*nv)
    c_scan.Divide(nh, nv)
    frame = {}
    for i, p in enumerate(par):
        c_scan.cd(i+1)
        frame[i] = p.frame()
        nll.plotOn(frame[i], RooFit.ShiftToZero(), RooFit.PrintEvalErrors(-1), RooFit.EvalErrorValue(nll.getVal()+10))
        frame[i].GetXaxis().SetRangeUser(p.getMin()*0.75, p.getMax()*1.5)
        frame[i].GetYaxis().SetRangeUser(0, 9)
        lmin = drawLine(p.getMin(), 0, p.getMin(), 9)
        lmax = drawLine(p.getMax(), 0, p.getMax(), 9)
        #c_scan.GetPad(i).SetLogx()
        #c_scan.GetPad(i).SetLogy()
        frame[i].Draw()
    c_scan.Print("Scan.pdf")
    #raw_input("Press Enter to continue...")
    #if options.bash: gROOT.SetBatch(True)
    
def reGenerate(dataset, pdf, variable):
    from ROOT import RooFit, RooArgSet
    # step 1: preliminary fit
    fr = pdf.fitTo(dataset, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
    # step 2: generate new dataset
    nev = dataset.sumEntries()
    nev = max(nev, 1000)
    dataset2 = pdf.generate(RooArgSet(variable), nev)
    #step 3: refit
    fr2 = pdf.fitTo(dataset2, RooFit.SumW2Error(False), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
    return pdf, fr2

def getColor(name, channel):
    color = {1 : [922, 920], 2 : [418, 410], 3 : [602, 590], 4 : [613, 609], 5 : [800, 400], }
    try:
        order = int(name[-1])
        if order in color: return color[order]
    except:
        name = name.replace('_'+channel, '').replace(channel, '')
        if 'total' in name: return [1, 1]
        elif 'Top' in name: return [798, 798]
        elif 'VV' in name: return [602, 602]
        elif 'Bkg' in name: return [590, 590]
        else:
            from samples import sample
            if name in sample.keys(): return [sample[name]['linecolor'], sample[name]['linecolor']]
    return [1, 1]

