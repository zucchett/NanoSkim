#! /usr/bin/env python

import os, sys, getopt, multiprocessing
import copy, math, pickle
from array import array
from ROOT import gROOT, gSystem, gStyle, gRandom
from ROOT import TMath, TFile, TChain, TTree, TCut, TH1F, TH2F, TF1, THStack, TGraph, TGraphErrors, TGaxis
from ROOT import TStyle, TCanvas, TPad, TLegend, TLatex, TText

# Import PDF library
from ROOT import RooFit, RooRealVar, RooDataHist, RooDataSet, RooAbsData, RooAbsReal, RooAbsPdf, RooPlot, RooBinning, RooCategory, RooSimultaneous, RooArgList, RooArgSet, RooWorkspace, RooMsgService
from ROOT import RooFormulaVar, RooGenericPdf, RooGaussian, RooExponential, RooPolynomial, RooChebychev, RooBreitWigner, RooCBShape, RooExtendPdf, RooAddPdf
gSystem.Load("PDFs/DSCB_cxx.so")
from ROOT import RooDoubleCrystalBall

from rooUtils import *
from plotUtils import *
from samples import sample

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-a", "--all", action="store_true", default=False, dest="all")
parser.add_option("-b", "--bash", action="store_true", default=False, dest="bash")
parser.add_option("-c", "--category", action="store", type="string", dest="category", default="")
parser.add_option("-d", "--test", action="store_true", default=False, dest="bias")
parser.add_option("-y", "--year", action="store", type="int", dest="year", default=0)
parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose")
(options, args) = parser.parse_args()
if options.bash: gROOT.SetBatch(True)

########## SETTINGS ##########

# Silent RooFit
RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)

#gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPadTopMargin(0.06)
gStyle.SetPadRightMargin(0.05)
gStyle.SetErrorX(0.)

NTUPLEDIR   = "/lustre/cmsdata/zucchett/Higgs/v1/Pico/"
PLOTDIR     = "fits/"
CARDDIR     = "datacards/"
WORKDIR     = "workspaces/"
RATIO       = 4
SHOWERR     = True
BLIND       = False
LUMI        = 137000
YEAR        = options.year
VERBOSE     = options.verbose
READTREE    = True
CUTCOUNT    = False
VARBINS     = False
BIAS        = options.bias

jobs = []

signalList = ['H', 'Z']
categoryList = {
    "EB" : "absPhoton_eta < 1.479",
    "EE" : "absPhoton_eta > 1.653",
}

XMIN = 60.
XZMIN = 86.
XZMAX = 96.
XHMIN = 120.
XHMAX = 130.
XMAX = 200.
XBINWIDTH = 1.
bins = [x+30 for x in range(int(XMIN), int(XMAX))]
abins = array( 'd', bins )

data = ["data_obs"]
back = ["DYJetsToLL", "QCD"]
sign = ["ZToJPsiG", "HToJPsiG"]

########## ######## ##########

def dijet(category):
    isData = True # Useful flag when running on MC
    baseCut = ""
    if not category in categoryList:
        print "Category not recognized."
        exit()
    baseCut = categoryList[category]
    
    pd = [x for x in sample['data_obs']['files'] if 'Charmonium' in x] #MuonEG
    if not os.path.exists(PLOTDIR+category): os.makedirs(PLOTDIR+category)
    if BIAS: print "Running in BIAS mode"
    
    order = 0
    RSS = {}
    
    X_mass     = RooRealVar(  "H_mass",    "m_{#mu#mu#gamma}", XMIN, XMAX, "GeV")
    JPsi_mass  = RooRealVar(  "JPsi_mass", "m_{#mu#mu}",       -9.,  1.e6, "GeV")
    Photon_eta = RooRealVar(  "absPhoton_eta", "#gamma #eta",   0.,  +2.5, ""   )
    weight     = RooRealVar(  "eventWeightLumi", "weight",   -1.e9,  1.e9       )
    variables  = RooArgSet(X_mass, JPsi_mass, Photon_eta)
    variables.add(RooArgSet(weight))
    
    X_mass.setRange("LowRange", XMIN, XZMIN)
    X_mass.setRange("ZRange",  XZMIN, XZMAX)
    X_mass.setRange("MedRange", XZMAX, XHMIN)
    X_mass.setRange("HRange",  XHMIN, XHMAX)
    X_mass.setRange("HighRange", XHMAX, XMAX)
    
    X_mass.setRange("FullRange", XMIN, XMAX)
    X_mass.setBins(int((X_mass.getMax()-X_mass.getMin())/XBINWIDTH))
    
    if BLIND: fitRanges = "LowRange,MedRange,HighRange"
    else: fitRanges = "FullRange"

    binsXmass = RooBinning(int((X_mass.getMax()-X_mass.getMin())/XBINWIDTH), X_mass.getMin(), X_mass.getMax())
    
    file = {}
    treeBkg = TChain("Events")
    for i, s in enumerate(data):
        for j, ss in enumerate(sample[s]['files']):
            if s in data and not ss in pd: continue
            if YEAR == 2016 and not ('Run2016' in ss or 'Summer16' in ss): continue
            if YEAR == 2017 and not ('Run2017' in ss or 'Fall17' in ss): continue
            if YEAR == 2018 and not ('Run2018' in ss or 'Autumn18' in ss): continue
            for f in os.listdir(NTUPLEDIR + '/' + ss): treeBkg.Add(NTUPLEDIR + '/' + ss + '/' + f)
    setData = RooDataSet("setData", "Data" if isData else "Data (QCD MC)", variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeBkg))
    
    nEvents = setData.sumEntries()
    
    print "Imported", ("data" if isData else "MC"), "RooDataSet with", nEvents#, "events between [%.1f, %.1f]" % (xmin, xmax)
    
    # 1 parameter
    p1_1 = RooRealVar("CMSRun2_"+category+"_p1_1", "p1", 7.0, 0., 1000.)
    #modelBkg1 = RooExponential("Bkg1", "Bkg. fit (1 par.)", X_mass, p1_1)
    modelBkg1 = RooGenericPdf("Bkg1", "Bkg. fit (2 par.)", "1./pow(@0/13000, @1)", RooArgList(X_mass, p1_1))
    normzBkg1 = RooRealVar(modelBkg1.GetName()+"_norm", "Number of background events", nEvents, 0., 1.e10)
    modelExt1 = RooExtendPdf(modelBkg1.GetName()+"_ext", modelBkg1.GetTitle(), modelBkg1, normzBkg1)
    fitRes1 = modelExt1.fitTo(setData, RooFit.Range(fitRanges), RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(not isData), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
    RSS[1] = drawFit("Bkg1", category, X_mass, modelBkg1, setData, binsXmass, [fitRes1], nEvents)
    fitRes1.Print()
    
    
    # 2 parameters
    p2_1 = RooRealVar("CMSRun2_"+category+"_p2_1", "p1", 0., -10000., 10000.)
    p2_2 = RooRealVar("CMSRun2_"+category+"_p2_2", "p2", p1_1.getVal(), -100., 600.)
    modelBkg2 = RooGenericPdf("Bkg2", "Bkg. fit (3 par.)", "pow(1-@0/13000, @1) / pow(@0/13000, @2)", RooArgList(X_mass, p2_1, p2_2))
    normzBkg2 = RooRealVar(modelBkg2.GetName()+"_norm", "Number of background events", nEvents, 0., 1.e10)
    modelExt2 = RooExtendPdf(modelBkg2.GetName()+"_ext", modelBkg2.GetTitle(), modelBkg2, normzBkg2)
    fitRes2 = modelExt2.fitTo(setData, RooFit.Range(fitRanges), RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(not isData), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
    RSS[2] = drawFit("Bkg2", category, X_mass, modelBkg2, setData, binsXmass, [fitRes2], nEvents)
    fitRes2.Print()
    
    # 3 parameters
    p3_1 = RooRealVar("CMSRun2_"+category+"_p3_1", "p1", p2_1.getVal(), -10000., 10000.)
    p3_2 = RooRealVar("CMSRun2_"+category+"_p3_2", "p2", p2_2.getVal(), -200., 1000.)
    p3_3 = RooRealVar("CMSRun2_"+category+"_p3_3", "p3", -2.5, -100., 100.)
    modelBkg3 = RooGenericPdf("Bkg3", "Bkg. fit (4 par.)", "pow(1-@0/13000, @1) / pow(@0/13000, @2+@3*log(@0/13000))", RooArgList(X_mass, p3_1, p3_2, p3_3))
    normzBkg3 = RooRealVar(modelBkg3.GetName()+"_norm", "Number of background events", nEvents, 0., 1.e10)
    modelExt3 = RooExtendPdf(modelBkg3.GetName()+"_ext", modelBkg3.GetTitle(), modelBkg3, normzBkg3)
    fitRes3 = modelExt3.fitTo(setData, RooFit.Range(fitRanges), RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(not isData), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
    RSS[3] = drawFit("Bkg3", category, X_mass, modelBkg3, setData, binsXmass, [fitRes3], nEvents)
    fitRes3.Print()
    
    # 4 parameters
    p4_1 = RooRealVar("CMSRun2_"+category+"_p4_1", "p1", p3_1.getVal(), -10000., 10000.)
    p4_2 = RooRealVar("CMSRun2_"+category+"_p4_2", "p2", p3_2.getVal(), -1000., 1000.)
    p4_3 = RooRealVar("CMSRun2_"+category+"_p4_3", "p3", p3_3.getVal(), -10., 10.)
    p4_4 = RooRealVar("CMSRun2_"+category+"_p4_4", "p4", 0.1, -10., 10.)
    modelBkg4 = RooGenericPdf("Bkg4", "Bkg. fit (5 par.)", "pow(1 - @0/13000, @1) / pow(@0/13000, @2+@3*log(@0/13000)+@4*pow(log(@0/13000), 2))", RooArgList(X_mass, p4_1, p4_2, p4_3, p4_4))
    normzBkg4 = RooRealVar(modelBkg4.GetName()+"_norm", "Number of background events", nEvents, 0., 1.e10)
    modelExt4 = RooExtendPdf(modelBkg4.GetName()+"_ext", modelBkg4.GetTitle(), modelBkg4, normzBkg4)
    fitRes4 = modelExt4.fitTo(setData, RooFit.Range(fitRanges), RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(not isData), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
    RSS[4] = drawFit("Bkg4", category, X_mass, modelBkg4, setData, binsXmass, [fitRes4], nEvents)
    fitRes4.Print()
    
    # Normalization parameters are should be set constant, but shape ones should not
#    if BIAS:
#        p1_1.setConstant(True)
#        p2_1.setConstant(True)
#        p2_2.setConstant(True)
#        p3_1.setConstant(True)
#        p3_2.setConstant(True)
#        p3_3.setConstant(True)
#        p4_1.setConstant(True)
#        p4_2.setConstant(True)
#        p4_3.setConstant(True)
#        p4_4.setConstant(True)
    normzBkg1.setConstant(True)
    normzBkg2.setConstant(True)
    normzBkg3.setConstant(True)
    normzBkg4.setConstant(True)
    
    #*******************************************************#
    #                                                       #
    #                         Fisher                        #
    #                                                       #
    #*******************************************************#
    
    # Fisher test
    print "-"*25
    print "function & $\\chi^2$ & RSS & ndof & F-test & result \\\\"
    print "\\multicolumn{6}{c}{", getChannel(category), "} \\\\"
    print "\\hline"
    for o1 in range(1, 5):
        o2 = min(o1 + 1, 5)
        print "%d par & %.2f & %.2f & %d & " % (o1+1, RSS[o1]["chi2"], RSS[o1]["rss"], RSS[o1]["nbins"]-RSS[o1]["npar"]),
        if o2 > len(RSS):
            print "\\\\"
            continue
        CL = fisherTest(RSS[o1]['rss'], RSS[o2]['rss'], o1+1, o2+1, RSS[o1]["nbins"])
        print "%d par vs %d par CL=%.2f & " % (o1+1, o2+1, CL),
        if CL > 0.10: # The function with less parameters is enough
            if not order:
                order = o1
                print "%d par are sufficient" % (o1+1),
                #break
        else:
            print "%d par are needed" % (o2+1),
            #order = o2
        print "\\\\"
    print "\\hline"
    print "-"*25   
    print "@ Order is", order, "("+category+")"
    
    if order==1:
        modelBkg = modelBkg1
        modelAlt = modelBkg2
        normzBkg = normzBkg1
        fitRes = fitRes1
    elif order==2:
        modelBkg = modelBkg2
        modelAlt = modelBkg3
        normzBkg = normzBkg2
        fitRes = fitRes2
    elif order==3:
        modelBkg = modelBkg3
        modelAlt = modelBkg4
        normzBkg = normzBkg3
        fitRes = fitRes3
    elif order==4:
        modelBkg = modelBkg4
        modelAlt = modelBkg3
        normzBkg = normzBkg4
        fitRes = fitRes4
    else:
        print "Functions with", order+1, "or more parameters are needed to fit the background"
        exit()
    
    modelBkg.SetName("Bkg_"+category)
    modelAlt.SetName("Alt_"+category)
    normzBkg.SetName("Bkg_"+category+"_norm")
    
    print "-"*25
    
    # Generate pseudo data
    setToys = RooDataSet()
    setToys.SetName("data_toys")
    setToys.SetTitle("Data (toys)")
    if BLIND:
        print " - Generating", nEvents, "events for toy data"
        if READTREE: setToys = modelAlt.generate(RooArgSet(X_mass), nEvents)
        else: setToys = modelAlt.generateBinned(RooArgSet(X_mass), nEvents)
        #fitRes = modelBkg.fitTo(setToys, RooFit.Range(fitRanges), RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(False), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
        

    #*******************************************************#
    #                                                       #
    #                    Signal shape                       #
    #                                                       #
    #*******************************************************#
    
    treeSign = {}
    setSignal = {}

    vmean  = {}
    vsigma = {}
    valpha1 = {}
    vslope1 = {}
    valpha2 = {}
    vslope2 = {}
    smean  = {}
    ssigma = {}
    salpha1 = {}
    sslope1 = {}
    salpha2 = {}
    sslope2 = {}
    sbrwig = {}
    signal = {}
    signalExt = {}
    signalYield = {}
    signalIntegral = {}
    signalNorm = {}
    signalXS = {}
    frSignal = {}
    frSignal1 = {}
    frSignal2 = {}
    frSignal3 = {}

    # Signal shape uncertainties (common amongst all mass points)
    xmean_fit = RooRealVar("sig_p1_fit", "Variation of the resonance position with the fit uncertainty", 0.005, -1., 1.)
    smean_fit = RooRealVar("CMSRun2_sig_p1_fit", "Change of the resonance position with the fit uncertainty", 0., -10, 10)
    xmean_m = RooRealVar("sig_p1_scale_m", "Variation of the resonance position with the muon energy scale", 0.0006, -1., 1.)
    smean_m = RooRealVar("CMSRun2_sig_p1_scale_m", "Change of the resonance position with the muon energy scale", 0., -10, 10)
    xmean_a = RooRealVar("sig_p1_scale_a", "Variation of the resonance position with the photon energy scale", 0.0006, -1., 1.)
    smean_a = RooRealVar("CMSRun2_sig_p1_scale_a", "Change of the resonance position with the photon energy scale", 0., -10, 10)

    xsigma_fit = RooRealVar("sig_p2_fit", "Variation of the resonance width with the fit uncertainty", 0.02, -1., 1.)
    ssigma_fit = RooRealVar("CMSRun2_sig_p2_fit", "Change of the resonance width with the fit uncertainty", 0., -10, 10)
    xsigma_m = RooRealVar("sig_p2_scale_m", "Variation of the resonance width with the muon energy scale", 0.010, -1., 1.)
    ssigma_m = RooRealVar("CMSRun2_sig_p2_scale_m", "Change of the resonance width with the muon energy scale", 0., -10, 10)
    xsigma_a = RooRealVar("sig_p2_scale_a", "Variation of the resonance width with the photon energy scale", 0.010, -1., 1.)
    ssigma_a = RooRealVar("CMSRun2_sig_p2_scale_a", "Change of the resonance width with the photon energy scale", 0., -10, 10)
    
    xalpha1_fit = RooRealVar("sig_p3_fit", "Variation of the resonance alpha with the fit uncertainty", 0.03, -1., 1.)
    salpha1_fit = RooRealVar("CMSRun2_sig_p3_fit", "Change of the resonance alpha with the fit uncertainty", 0., -10, 10)
    
    xslope1_fit = RooRealVar("sig_p4_fit", "Variation of the resonance slope with the fit uncertainty", 0.10, -1., 1.)
    sslope1_fit = RooRealVar("CMSRun2_sig_p4_fit", "Change of the resonance slope with the fit uncertainty", 0., -10, 10)
    
    xalpha2_fit = RooRealVar("sig_p5_fit", "Variation of the resonance alpha 2 with the fit uncertainty", 0.03, -1., 1.)
    salpha2_fit = RooRealVar("CMSRun2_sig_p5_fit", "Change of the resonance alpha 2 with the fit uncertainty", 0., -10, 10)
    
    xslope2_fit = RooRealVar("sig_p6_fit", "Variation of the resonance slope 2 with the fit uncertainty", 0.10, -1., 1.)
    sslope2_fit = RooRealVar("CMSRun2_sig_p6_fit", "Change of the resonance slope 2 with the fit uncertainty", 0., -10, 10)

    xmean_fit.setConstant(True)
    smean_fit.setConstant(True)
    xmean_m.setConstant(True)
    smean_m.setConstant(True)
    xmean_a.setConstant(True)
    smean_a.setConstant(True)
    
    xsigma_fit.setConstant(True)
    ssigma_fit.setConstant(True)
    xsigma_m.setConstant(True)
    ssigma_m.setConstant(True)
    xsigma_a.setConstant(True)
    ssigma_a.setConstant(True)
    
    xalpha1_fit.setConstant(True)
    salpha1_fit.setConstant(True)
    xslope1_fit.setConstant(True)
    sslope1_fit.setConstant(True)
    
    xalpha2_fit.setConstant(True)
    salpha2_fit.setConstant(True)
    xslope2_fit.setConstant(True)
    sslope2_fit.setConstant(True)

    
    #if not isSB:
    for i, s in enumerate(sign):
    
        # Read trees
        treeSign[s] = TChain("Events")
        for j, ss in enumerate(sample[s]['files']):
            if s in data and not ss in pd: continue
            if YEAR == 2016 and not ('Run2016' in ss or 'Summer16' in ss): continue
            if YEAR == 2017 and not ('Run2017' in ss or 'Fall17' in ss): continue
            if YEAR == 2018 and not ('Run2018' in ss or 'Autumn18' in ss): continue
            for f in os.listdir(NTUPLEDIR + '/' + ss): treeSign[s].Add(NTUPLEDIR + '/' + ss + '/' + f)
        setSignal[s] = RooDataSet("set" + s, s, variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeSign[s]))
        if VERBOSE: print " - Dataset with", setSignal[s].sumEntries(), "events loaded"
    
        # Build model
        signalName = s[0] + "_" + category
        m = 91.2 if s[0].startswith("Z") else 125.
        
        # define the signal PDF
        vmean[s] = RooRealVar(signalName + "_vmean", "Crystal Ball mean", m, m*0.95, m*1.05)
        smean[s] = RooFormulaVar(signalName + "_mean", "@0*(1+@1*@2)*(1+@3*@4)*(1+@5*@6)", RooArgList(vmean[s], xmean_fit, smean_fit, xmean_m, smean_m, xmean_a, smean_a))

        vsigma[s] = RooRealVar(signalName + "_vsigma", "Crystal Ball sigma", m*0.01, m*0., m*0.1)
        ssigma[s] = RooFormulaVar(signalName + "_sigma", "@0*(1+@1*@2)*(1+@3*@4)*(1+@5*@6)", RooArgList(vsigma[s], xsigma_fit, ssigma_fit, xsigma_m, ssigma_m, xsigma_a, ssigma_a))
        
        valpha1[s] = RooRealVar(signalName + "_valpha1", "Crystal Ball alpha", 1.,  0., 5.) # number of sigmas where the exp is attached to the gaussian core. >0 left, <0 right
        salpha1[s] = RooFormulaVar(signalName + "_alpha1", "@0*(1+@1*@2)", RooArgList(valpha1[s], xalpha1_fit, salpha1_fit))

        vslope1[s] = RooRealVar(signalName + "_vslope1", "Crystal Ball slope", 3., 0., 110.) # slope of the power tail
        sslope1[s] = RooFormulaVar(signalName + "_slope1", "@0*(1+@1*@2)", RooArgList(vslope1[s], xslope1_fit, sslope1_fit))
        
        valpha2[s] = RooRealVar(signalName + "_valpha2", "Crystal Ball alpha 2", 1.,  0., 5.) # number of sigmas where the exp is attached to the gaussian core. >0 left, <0 right
        salpha2[s] = RooFormulaVar(signalName + "_alpha2", "@0*(1+@1*@2)", RooArgList(valpha2[s], xalpha2_fit, salpha2_fit))

        vslope2[s] = RooRealVar(signalName + "_vslope2", "Crystal Ball slope 2", 3., 0., 110.) # slope of the power tail
        sslope2[s] = RooFormulaVar(signalName + "_slope2", "@0*(1+@1*@2)", RooArgList(vslope2[s], xslope2_fit, sslope2_fit))

#        smean[s] = RooRealVar(signalName + "_mean" , "mean of the Crystal Ball", m, m*0.8, m*1.2)
#        ssigma[s] = RooRealVar(signalName + "_sigma", "Crystal Ball sigma", m*0.04, m*0.001, m*0.2)
#        salpha1[s] = RooRealVar(signalName + "_alpha1", "Crystal Ball alpha", 1,  0., 5.) # number of sigmas where the exp is attached to the gaussian core. >0 left, <0 right
#        sslope1[s] = RooRealVar(signalName + "_slope1", "Crystal Ball slope", 20, 10., 60.) # slope of the power tail
#        salpha2[s] = RooRealVar(signalName + "_alpha2", "Crystal Ball alpha", 2,  1., 5.) # number of sigmas where the exp is attached to the gaussian core. >0 left, <0 right
#        sslope2[s] = RooRealVar(signalName + "_slope2", "Crystal Ball slope", 10, 1.e-1, 115.) # slope of the power tail


        signal[s] = RooDoubleCrystalBall(signalName, "Double Crystal Ball", X_mass, smean[s], ssigma[s], salpha1[s], sslope1[s], salpha2[s], sslope2[s]) # Signal name does not have the channel
#        signal[s] = RooCBShape(signalName, "m_{%s'} = %d GeV" % (s, m), X_mass, smean[s], ssigma[s], salpha1[s], sslope1[s]) # Signal name does not have the channel
        #signal[s] = RooGaussian(signalName, "m_{%s'} = %d GeV" % (s, m), X_mass, smean[s], ssigma[s])

        # extend the PDF with the yield to perform an extended likelihood fit
        signalYield[s] = RooRealVar(signalName+"_yield", "signalYield", 100, 0., 1.e6)
        signalNorm[s] = RooRealVar(signalName+"_norm", "signalNorm", 1., 0., 1.e6)
        signalXS[s] = RooRealVar(signalName+"_xs", "signalXS", 1., 0., 1.e6)
        signalExt[s] = RooExtendPdf(signalName+"_ext", "extended p.d.f", signal[s], signalYield[s])
    
    
        # Fit
        signalYield[s].setVal(setSignal[s].sumEntries())
        frSignal[s] = signalExt[s].fitTo(setSignal[s], RooFit.Range("FullRange"), RooFit.Save(1), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Extended(True), RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
        if VERBOSE: print "********** Fit result [", m, "] **", category, "*"*40, "\n", frSignal[s].Print(), "\n", "*"*80
        if VERBOSE: frSignal[s].correlationMatrix().Print()
        rss = drawFit(s, category, X_mass, signal[s], setSignal[s], binsXmass)
        
        signalNorm[s].setVal( signalYield[s].getVal() * sample[s]['weight'])
    
        vmean[s].setConstant(True)
        vsigma[s].setConstant(True)
        valpha1[s].setConstant(True)
        vslope1[s].setConstant(True)
        valpha2[s].setConstant(True)
        vslope2[s].setConstant(True)
        signalNorm[s].setConstant(True)
        signalXS[s].setConstant(True)
    
        
        #*******************************************************#
        #                                                       #
        #                      Datacard                         #
        #                                                       #
        #*******************************************************#

        card  = "imax 1\n"
        card += "jmax *\n"
        card += "kmax *\n"
        card += "-----------------------------------------------------------------------------------\n"
        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % (signalName, category, WORKDIR, category, "XJPsiGamma:$PROCESS")
        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % (modelBkg.GetName(), category, WORKDIR, category, "XJPsiGamma:$PROCESS")
        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % ("data_obs", category, WORKDIR, category, "XJPsiGamma:data_obs")
        card += "-----------------------------------------------------------------------------------\n"
        card += "bin               %s\n" % category
        card += "observation       %0.f\n" % (-1.)
        card += "-----------------------------------------------------------------------------------\n"
        card += "bin                                     %-20s%-20s\n" % (category, category)
        card += "process                                 %-20s%-20s\n" % (signalName, modelBkg.GetName()) #"roomultipdf"
        card += "process                                 %-20s%-20s\n" % ("0", "1")
        card += "rate                                    %-20d%-20f\n" % (1, 1) #signalYield[m].getVal(), nEvents
        card += "-----------------------------------------------------------------------------------\n"
        for p in range(1, order+1): card += "%-35s     flatParam\n" % ("CMSRun2_"+category+"_p%d_%d" % (order, p))
        card += "%-35s     lnU       %-20s%-20.0f\n" % ("CMSRun2_"+category+"_norm",    "-", 4.)
        card += "%-35s     lnN       %-20.4f%-20s\n" % ("CMSRun2_eff_trigger",    1.040, "-")
        card += "%-35s     lnN       %-20.4f%-20s\n" % ("CMSRun2_eff_m",    1.030 if signalName=="Z" else 1.020, "-")
        card += "%-35s     lnN       %-20.4f%-20s\n" % ("CMSRun2_eff_a",    1.012, "-")
        card += "%-35s     lnN       %-20.4f%-20s\n" % ("CMSRun2_eff_e",    1.010, "-")
        card += "%-35s     lnN       %-20.4f%-20s\n" % ("CMSRun2_scale_pu",    1.008, "-")
        card += "%-35s     lnN       %-20.4f%-20s\n" % ("CMSRun2_lumi",    1.025, "-")
        card += "%-35s     lnN       %-20.4f%-20s\n" % ("pdf_scale", 1.017 if signalName=="Z" else 1.032, "-")
        card += "%-35s     lnN       %-20.4f%-20s\n" % ("qcd_scale", 1.035 if signalName=="Z" else 1.056, "-")
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p1_fit", 0, 1)
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p1_scale_m", 0, 1)
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p1_scale_a", 0, 1)
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p2_fit", 0, 1)
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p2_scale_m", 0, 1)
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p2_scale_a", 0, 1)
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p3_fit", 0, 1)
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p4_fit", 0, 1)
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p5_fit", 0, 1)
        card += "%-35s     param %.1f %.1f\n" % ("CMSRun2_sig_p6_fit", 0, 1)

        '''
        # log-normal uncertainties
        for s in sorted(syst):
            if type(syst[s]) == dict:
                sy = syst[s].get(m, syst[s][min(syst[s].keys(), key=lambda k: abs(k-m))])
                card += "%-35s     lnN       %-20s%-20s\n" % (s.replace('_migration', ''), "%.3f/%.3f" % (sy[0], sy[1]), "-")
            elif type(syst[s]) == list: card += "%-35s     lnN       %-20s%-20s\n" % (s, "%.3f/%.3f" % (1.+syst[s][0], 1.+syst[s][1]), "-")
            else: card += "%-35s     lnN       %-20.3f%-20s\n" % (s,    1.+syst[s], "-")
            
        # uncertanty groups
        card += "theory group = pdf_scale qcd_scale\n"
        card += "norm group = CMSRun2_"+category+"_norm\n"
        if isShape:
            card += "shape group = "
            for p in range(1, order+1): card += "CMSRun2_"+category+"_p%d_%d " % (order, p)
            card += "\n"
            card += "shapeS group = "
            for i in syst_sig.keys(): card += i + " "
            card += "\n"
        
        for s in signalList:
            if s == stype: outcard = card
            else: outcard = card.replace(stype, s)
        '''
        outname = CARDDIR+"/%s_%s.txt" % (s, category)
        cardfile = open(outname, 'w')
        cardfile.write(card)
        cardfile.close()
        #print "Datacards for mass", m, "in category", category, "saved in", outname
        '''
        if BIAS:
            outcard = card.replace(modelBkg.GetName(), "roomultipdf")
            outcard.replace("rate                                    %-20.6f%-20.6f\n" % (1, 1), "rate                                    %-20.6f%-20.6f\n" % (10, 1))
            outcard += "%-35s     discrete\n" % ("pdf_index")
            outname = CARDDIR+"bias/%s%s_M%d.txt" % (stype, category, m)
            cardfile = open(outname, 'w')
            cardfile.write(outcard)
            cardfile.close()
        '''

    #*******************************************************#
    #                                                       #
    #                   Generate workspace                  #
    #                                                       #
    #*******************************************************#
    
    if BIAS:
        gSystem.Load("libHiggsAnalysisCombinedLimit.so")
        from ROOT import RooMultiPdf
        cat = RooCategory("pdf_index", "Index of Pdf which is active");
        pdfs = RooArgList(modelBkg, modelAlt)
        roomultipdf = RooMultiPdf("roomultipdf", "All Pdfs", cat, pdfs)
        normulti = RooRealVar("roomultipdf_norm", "Number of background events", nEvents, 0., 1.e6)
    
    # create workspace
    w = RooWorkspace("XJPsiGamma", "workspace")
    # Dataset
    if not BLIND: getattr(w, "import")(setData, RooFit.Rename("data_obs"))
    else: getattr(w, "import")(setToys, RooFit.Rename("data_obs"))
    if BIAS:
        getattr(w, "import")(cat, RooFit.Rename(cat.GetName()))
        getattr(w, "import")(normulti, RooFit.Rename(normulti.GetName()))
        getattr(w, "import")(roomultipdf, RooFit.Rename(roomultipdf.GetName()))
    getattr(w, "import")(modelBkg, RooFit.Rename(modelBkg.GetName()))
    getattr(w, "import")(modelAlt, RooFit.Rename(modelAlt.GetName()))
    getattr(w, "import")(normzBkg, RooFit.Rename(normzBkg.GetName()))
    for s in sign:
        getattr(w, "import")(signal[s], RooFit.Rename(signal[s].GetName()))
        getattr(w, "import")(signalNorm[s], RooFit.Rename(signalNorm[s].GetName()))
    #getattr(w, "import")(roomultipdf, RooFit.Rename(roomultipdf.GetName()))
    #w.Print()
    w.writeToFile("%s/%s.root" % (WORKDIR, category), True)
    print "Workspace", "%s/%s.root" % (WORKDIR, category), "saved successfully"
    
    if VERBOSE: raw_input("Press Enter to continue...")
    
    
    
    #*******************************************************#
    #                                                       #
    #                         Plot                          #
    #                                                       #
    #*******************************************************#
    
    c = TCanvas("c_"+category, category, 800, 800)
    c.Divide(1, 2)
    setTopPad(c.GetPad(1), RATIO)
    setBotPad(c.GetPad(2), RATIO)
    c.cd(1)
    frame = X_mass.frame()
    setPadStyle(frame, 1.25, True)
    if VARBINS: frame.GetXaxis().SetRangeUser(X_mass.getMin(), X_mass.getMax())
    

    graphData = setData.plotOn(frame, RooFit.Binning(binsXmass), RooFit.Invisible())
    #if BLIND: setToys.plotOn(frame, RooFit.Binning(binsXmass), RooFit.MarkerColor(2), RooFit.LineColor(2), RooFit.MarkerStyle(24))
    modelBkg.plotOn(frame, RooFit.Normalization(nEvents, RooAbsReal.NumEvent), RooFit.VisualizeError(fitRes, 1, False), RooFit.LineColor(602), RooFit.FillColor(590), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Name("1sigma"))
    modelBkg.plotOn(frame, RooFit.Normalization(nEvents, RooAbsReal.NumEvent), RooFit.LineColor(602), RooFit.FillColor(590), RooFit.FillStyle(1001), RooFit.DrawOption("L"), RooFit.Name(modelBkg.GetName()))
    modelAlt.plotOn(frame, RooFit.Normalization(nEvents, RooAbsReal.NumEvent), RooFit.LineStyle(7), RooFit.LineColor(613), RooFit.FillColor(609), RooFit.FillStyle(1001), RooFit.DrawOption("L"), RooFit.Name(modelAlt.GetName()))
    for s in sign:
        signal[s].plotOn(frame, RooFit.Normalization(signalNorm[s].getVal(), RooAbsReal.NumEvent), RooFit.LineStyle(1), RooFit.LineWidth(3), RooFit.LineColor(getColor(s, category)[0]), RooFit.DrawOption("L"), RooFit.Name(s))
    graphData = setData.plotOn(frame, RooFit.Binning(binsXmass), RooFit.XErrorSize(0 if not VARBINS else 1), RooFit.DataError(RooAbsData.Poisson if isData else RooAbsData.SumW2), RooFit.DrawOption("PE0"), RooFit.Name(setData.GetName()))
    fixData(graphData.getHist(), [[XZMIN, XZMAX], [XHMIN, XHMAX]] if BLIND else [], True, True, not isData)
    pulls = frame.pullHist(setData.GetName(), modelBkg.GetName(), True)
    chi = frame.chiSquare(setData.GetName(), modelBkg.GetName(), True)
    #setToys.plotOn(frame, RooFit.DataError(RooAbsData.Poisson), RooFit.DrawOption("PE0"), RooFit.MarkerColor(2))
    if VARBINS: frame.GetYaxis().SetTitle("Events / ( %d GeV )" % (XBINWIDTH,) )
    frame.Draw()
    
    frame.SetMaximum(frame.GetMaximum()*1.25)
    frame.SetMinimum(max(frame.GetMinimum(), 1.e-1))
    #c.GetPad(1).SetLogy()
    
    boxZ = drawBox(XZMIN, frame.GetMinimum(), XZMAX, frame.GetMaximum()/1.30, "Z")
#    lineL = drawLine(LOWMAX, frame.GetMinimum(), LOWMAX, frame.GetMaximum()/1.30)
#    lineM = drawLine(SIGMIN, frame.GetMinimum(), SIGMIN, frame.GetMaximum()/1.30)
#    lineU = drawLine(SIGMAX, frame.GetMinimum(), SIGMAX, frame.GetMaximum()/1.30)
    boxH = drawBox(XHMIN, frame.GetMinimum(), XHMAX, frame.GetMaximum()/1.30, "H")
#    textL = drawText((LOWMAX+LOWMIN)/2, frame.GetMaximum()/1.35, "LSB")
#    textV = drawText((SIGMIN+LOWMAX)/2, frame.GetMaximum()/1.35, "VR")
#    textH = drawText((SIGMAX+SIGMIN)/2, frame.GetMaximum()/1.35, "SR")
#    textU = drawText(HIGMIN+10, frame.GetMaximum()/1.35, "HSB")
    
    drawAnalysis(category)
    drawRegion(category, True)
    drawCMS(LUMI, "Preliminary")
    
    leg = TLegend(0.575, 0.6, 0.95, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.AddEntry(setData.GetName(), setData.GetTitle()+" (%d events)" % nEvents, "PEL")
    #leg.AddEntry(modelBkg1.GetName(), "Bkg. fit (1 par.)", "L")
    leg.AddEntry(modelBkg.GetName(), modelBkg.GetTitle(), "FL")#.SetTextColor(629)
    leg.AddEntry(modelAlt.GetName(), modelAlt.GetTitle(), "L")
    #leg.AddEntry(modelBkg4.GetName(), "Bkg. fit (4 par.)", "L")
    for s in sign: leg.AddEntry(s, sample[s]['label'], "L")
    leg.SetY1(0.9-leg.GetNRows()*0.05)
    leg.Draw()
    
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    latex.SetTextFont(42)
    
    c.cd(2)
    frame_res = X_mass.frame()
    setPadStyle(frame_res, 1.25)
    frame_res.addPlotable(pulls, "P")
    setBotStyle(frame_res, RATIO, False)
    if VARBINS: frame_res.GetXaxis().SetRangeUser(X_mass.getMin(), X_mass.getMax())
    frame_res.GetYaxis().SetRangeUser(-5, 5)
    frame_res.GetYaxis().SetTitle("(N^{data}-N^{bkg})/#sigma")
    frame_res.Draw()
    fixData(pulls, [[XZMIN, XZMAX], [XHMIN, XHMAX]] if BLIND else [], False, True, False)
    
    drawChi2(RSS[order]["chi2"], RSS[order]["nbins"]-(order+1), True)
    line = drawLine(X_mass.getMin(), 0, X_mass.getMax(), 0)
    
    c.SaveAs(PLOTDIR+category+"/Bkg_"+category+".pdf")
    c.SaveAs(PLOTDIR+category+"/Bkg_"+category+".png")
    
    # ======   END PLOT   ======
    


def fisherTest(RSS1, RSS2, o1, o2, N):
    #print "Testing functions with parameters", o1, "and", o2, "with RSS", RSS1, "and", RSS2
    #if (RSS1-RSS2)/(RSS2) < 0.125: return True
    #return (RSS1-RSS2)/RSS1 < (o2-o1)/o1
    dof1 = N - o1
    dof2 = N - o2
    n1 = N - dof1 - 1
    n2 = N - dof2 - 1
    F = ((RSS1-RSS2)/(n2-n1)) / (RSS2/(N-n2))
    #F_dist = TF1("F_distr", "TMath::Sqrt( (TMath::Power([0]*x,[0]) * TMath::Power([1],[1])) / (TMath::Power([0]*x + [1],[0]+[1])) ) / (x*TMath::Beta([0]/2,[1]/2))", 0, 1000)
    #F_dist.SetParameter(0, n2-n1)
    #F_dist.SetParameter(1, N-n2)
    #CL = 1 - F_dist.Integral(0.00000001, F)
    CL =  1.-TMath.FDistI(F, n2-n1, N-n2)
    #print F, N, n2-n1, N-n2, TMath.FDistI(F, n2-n1, N-n2)
    #print "F-test:", o1+1, "par vs", o2, "par & : F =", F, ", CL = %.4f" % CL
    
    return CL



def drawFit(name, category, variable, model, dataset, binning, fitRes=[], norm=-1):
    isData = ('Data' in dataset.GetTitle())
    npar = fitRes[0].floatParsFinal().getSize() if len(fitRes)>0 else 0
    varArg = RooArgSet(variable)
    
    c = TCanvas("c_"+category, category, 800, 800)
    c.Divide(1, 2)
    setTopPad(c.GetPad(1), RATIO)
    setBotPad(c.GetPad(2), RATIO)
    c.cd(1)
    frame = variable.frame()
    setPadStyle(frame, 1.25, True)
    dataset.plotOn(frame, RooFit.Binning(binning), RooFit.Invisible())
    if len(fitRes) > 0: model.plotOn(frame, RooFit.VisualizeError(fitRes[0], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), RooAbsReal.NumEvent), RooFit.LineColor(getColor(name, category)[0]), RooFit.FillColor(getColor(name, category)[1]), RooFit.FillStyle(1001), RooFit.DrawOption("FL"))
    model.plotOn(frame, RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), RooAbsReal.NumEvent), RooFit.LineColor(getColor(name, category)[0]), RooFit.FillColor(getColor(name, category)[1]), RooFit.FillStyle(1001), RooFit.DrawOption("L"), RooFit.Name(model.GetName()))
    model.paramOn(frame, RooFit.Label(model.GetTitle()), RooFit.Layout(0.55 if name in sign else 0.45, 0.95, 0.94), RooFit.Format("NEAU"))
    graphData = dataset.plotOn(frame, RooFit.Binning(binning), RooFit.DataError(RooAbsData.Poisson if isData else RooAbsData.SumW2), RooFit.DrawOption("PE0"), RooFit.Name(dataset.GetName()))
    if isData: fixData(graphData.getHist(), [[XZMIN, XZMAX], [XHMIN, XHMAX]] if BLIND else [], True, True, not isData)
    pulls = frame.pullHist(dataset.GetName(), model.GetName(), True)
    residuals = frame.residHist(dataset.GetName(), model.GetName(), False, True) # this is y_i - f(x_i)
    roochi2 = frame.chiSquare()
    frame.SetMaximum(frame.GetMaximum()*1.25)
    frame.SetMinimum(max(frame.GetMinimum(), 0.)) #1.e-2
    #c.GetPad(1).SetLogy()
    frame.Draw()
    
    drawAnalysis(category)
    drawRegion(category, True)
    drawCMS(LUMI, "Preliminary")
    
    c.cd(2)
    frame_res = variable.frame()
    setPadStyle(frame_res, 1.25)
    frame_res.addPlotable(pulls, "P")
    setBotStyle(frame_res, RATIO, False)
    frame_res.GetYaxis().SetRangeUser(-5, 5)
    frame_res.GetYaxis().SetTitle("(N^{data}-N^{bkg})/#sigma")
    frame_res.GetYaxis().SetTitleOffset(0.4)
    frame_res.Draw()
    if isData: fixData(pulls, [[XZMIN, XZMAX], [XHMIN, XHMAX]]  if BLIND else [], False, True, False)
    
    # calculate RSS
    nbins, res, rss, chi1, chi2 = 0, 0., 0., 0., 0.
    hist = graphData.getHist()
    xmin, xmax = array('d', [0.]), array('d', [0.])
    dataset.getRange(variable, xmin, xmax)
    for i in range(len(residuals.GetY())):
        if hist.GetX()[i] - hist.GetErrorXlow(i) > xmax[0] and hist.GetX()[i] + hist.GetErrorXhigh(i) > xmax[0]: continue# and abs(pulls.GetY()[i]) < 5:
        if hist.GetY()[i] <= 0.: continue
        res += residuals.GetY()[i]
        rss += residuals.GetY()[i]**2
        #print i, pulls.GetY()[i]
        chi1 += abs(pulls.GetY()[i])
        chi2 += pulls.GetY()[i]**2
        nbins = nbins + 1
    rss = math.sqrt(rss)
    out = {"chi2" : chi2, "chi1" : chi1, "rss" : rss, "res" : res, "nbins" : nbins, "npar" : npar}
    drawChi2(chi2, binning.numBins() - npar)
    line = drawLine(variable.getMin(), 0, variable.getMax(), 0)
    
    if len(name) > 0 and len(category) > 0:
        c.SaveAs(PLOTDIR+category+"/"+name+".pdf")
        c.SaveAs(PLOTDIR+category+"/"+name+".png")
    
    return out





if __name__ == "__main__":
    if options.all:
        for c in categoryList:#+controlList:
            dijet(c)
#            p = multiprocessing.Process(target=dijet, args=(c,))
#            jobs.append(p)
#            p.start()
    else:
        if any(x in options.category[3:] for x in categoryList+controlList) or any(x in options.category for x in categoryList+controlList): dijet(options.category)
        else:
            print "Category not set or not recognized. Quitting..."
            exit()

