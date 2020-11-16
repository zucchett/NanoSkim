#!/usr/bin/env python

import os, sys, getopt, multiprocessing
import copy, math, pickle
from array import array

from ROOT import gROOT, gSystem, gStyle, gRandom
from ROOT import TMath, TFile, TChain, TTree, TCut, TH1F, TH2F, THStack, TGraph, TGaxis
from ROOT import TStyle, TCanvas, TPad, TLegend, TLatex, TText, TColor
from ROOT import TH1, TF1, TGraph, TGraphErrors, TGraphAsymmErrors, TVirtualFitter

gSystem.Load("PDFs/HWWLVJRooPdfs_cxx.so")
from ROOT import RooFit, RooRealVar, RooDataHist, RooDataSet, RooAbsData, RooAbsReal, RooAbsPdf, RooPlot, RooBinning, RooCategory, RooSimultaneous, RooArgList, RooArgSet, RooWorkspace, RooMsgService
from ROOT import RooFormulaVar, RooGenericPdf, RooGaussian, RooExponential, RooPolynomial, RooChebychev, RooBreitWigner, RooCBShape, RooDoubleCrystalBall, RooExtendPdf, RooAddPdf

from alpha import drawPlot
from rooUtils import *
from samples import sample
from selections import selection


import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-a", "--all", action="store_true", default=False, dest="all")
parser.add_option("-b", "--bash", action="store_true", default=False, dest="bash")
parser.add_option("-c", "--channel", action="store", type="string", dest="channel", default="")
parser.add_option("-s", "--signal", action="store", type="string", dest="signal", default="")
parser.add_option("-e", "--efficiency", action="store_true", default=False, dest="efficiency")
parser.add_option("-p", "--parallelize", action="store_true", default=False, dest="parallelize")
parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose")
(options, args) = parser.parse_args()
if options.bash: gROOT.SetBatch(True)

colour = [
    TColor(1001, 0., 0., 0., "black", 1.),
    TColor(1002, 230./255, 159./255, 0., "orange", 1.),
    TColor(1003, 86./255, 180./255, 233./255, "skyblue", 1.),
    TColor(1004, 0., 158./255, 115./255, "bluishgreen", 1.),
    TColor(1005, 0., 114./255, 178./255, "blue", 1.),
    TColor(1006, 213./255, 94./255, 0., "vermillion", 1.),
    TColor(1007, 204./255, 121./255, 167./255, "reddishpurple", 1.),
]

########## SETTINGS ##########

# Silent RooFit
RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)

#gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPadTopMargin(0.06)
gStyle.SetPadRightMargin(0.05)
gStyle.SetErrorX(0.)

NTUPLEDIR   = "/scratch/zucchett/Ntuple/VH/"
PLOTDIR     = "plotsSignal/"
CARDDIR     = "datacards/"
WORKDIR     = "workspace/"
RATIO       = 4
LUMI        = 35867
VERBOSE     = options.verbose
PARALLELIZE = True
READTREE    = True


#channelList = ['nnb', 'nnbb']
#channelList = ['wrhpb', 'wrhpbb', 'wrlpb', 'wrlpbb', 'zrhpb', 'zrhpbb', 'zrlpb', 'zrlpbb'] #, 'wrhphp', 'wrhplp', 'wrlphp', 'wrlplp', 'zrhphp', 'zrhplp', 'zrlphp', 'zrlplp']
channelList = ['nnb', 'nnbb', 'enb', 'enbb', 'mnb', 'mnbb', 'eeb', 'eebb', 'mmb', 'mmbb']
#channelList = ['nnb', 'nnbb', 'enb', 'enbb', 'mnb', 'mnbb', 'eeb', 'eebb', 'mmb', 'mmbb', 'wrhpb', 'wrhpbb', 'wrlpb', 'wrlpbb', 'zrhpb', 'zrhpbb', 'zrlpb', 'zrlpbb']
#signalList = ['XWH', 'XZH', 'XVH']
signalList = ['AZh', 'BBAZh']

color = {'nnb' : 634, 'nnbb' : 634, 'enb' : 410, 'enbb' : 410, 'mnb' : 856, 'mnbb' : 856, 'eeb' : 418, 'eebb' : 418, 'mmb' : 602, 'mmbb' : 602, 'wrhpb': 634, 'wrhpbb': 634, 'wrlpb': 826, 'wrlpbb': 826, 'zrhpb': 856, 'zrhpbb': 856, 'zrlpb': 602, 'zrlpbb': 602, 'vrbbb' : 800, 'vrbbbb' : 801}


jobs = []

def signal(channel, stype):
    
    # HVT model
    if stype.startswith('X'):
        signalType = 'HVT'
        genPoints = [800, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000, 3500, 4000, 4500]
        massPoints = [x for x in range(800, 4500+1, 100)]
        interPar = True
    # 2HDM
    elif stype.startswith('A') or stype.startswith('BBA'):
        signalType = '2HDM'
        genPoints = [750, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000]
        massPoints = [x for x in range(750, 2000+1, 50)]
        interPar = True
        if not 'nn' in channel and not 'ee' in channel and not 'mm' in channel:
            print "Channel", channel, "not supported for signal", stype
            return
    # mono-Higgs
    elif stype.startswith('monoH'):
        signalType = 'monoH'
        genPoints = [[800, 300], [800, 400], [800, 500], [800, 600], 
            [1000, 300], [1000, 400], [1000, 500], [1000, 600], [1000, 700], [1000, 800], 
            [1200, 300], [1200, 400], [1200, 500], [1200, 600], [1200, 700], [1200, 800], 
            [1400, 300], [1400, 400], [1400, 500], [1400, 600], [1400, 700], [1400, 800], 
            [1700, 300], [1700, 400], [1700, 500], [1700, 600], [1700, 700], [1700, 800], 
            [2000, 300], [2000, 400], [2000, 500], [2000, 600], [2000, 700], [2000, 800], 
            [2500, 300], [2500, 400], [2500, 500], [2500, 600], [2500, 700], [2500, 800], 
            [3000, 300], [3000, 500], [3000, 800], 
            [3500, 300], [3500, 500], [3500, 800], 
            [4000, 300], [4000, 500], [4000, 800], 
        ]
        massPoints = genPoints
        interPar = False
        if not 'nn' in channel:
            print "Channel", channel, "not supported for signal", stype
            return
    else:
        print "Signal type", stype, "not recognized"
        return
    
    n = len(genPoints)  
    
    category = channel
    cColor = color[category] if category in color else 1

    nElec = channel.count('e')
    nMuon = channel.count('m')
    nLept = nElec + nMuon
    nBtag = channel.count('b')
    isHP = 'hp' in channel or nBtag > 2
    isLP = 'lp' in channel or nBtag > 2
    isAH = isHP or isLP
    
    X_name = "JJ_mass" if isAH else "VH_mass"

#    if nLept==1 and stype=='XZH': return
#    if nLept!=1 and stype=='XWH': return

    if not os.path.exists(PLOTDIR+stype+category): os.makedirs(PLOTDIR+stype+category)

    #*******************************************************#
    #                                                       #
    #              Variables and selections                 #
    #                                                       #
    #*******************************************************#
    X_mass  = RooRealVar ( X_name,      "m_{Vh}",            0., 5000., "GeV")
    J_mass  = RooRealVar( "H_mass", "H jet mass",          105.,  135., "GeV")
    V_mass  = RooRealVar( "V_mass", "V jet mass",           -9.,  1.e6, "GeV")
    CSV1    = RooRealVar( "H_csv1",           "",         -999.,     2.     )
    CSV2    = RooRealVar( "H_csv2",           "",         -999.,     2.     )
    H_ntag  = RooRealVar( "H_ntag",           "",           -9.,     9.     )
    H_dbt   = RooRealVar( "H_dbt",            "",           -2.,     2.     )
    H_tau21 = RooRealVar( "H_tau21",          "",           -9.,     2.     )
    V_tau21 = RooRealVar( "V_tau21",          "",           -9.,     2.     )
    V_dbt   = RooRealVar( "V_dbt",            "",           -2.,     2.     )
    MaxBTag = RooRealVar( "MaxBTag",          "",          -10.,     2.     )
    MinDPhi = RooRealVar( "MinDPhi",          "",           -1.,    99.     )
    DEta    = RooRealVar( "DEta",             "",           -1.,    99.     )
    nTaus   = RooRealVar( "nTaus",            "",           -1.,    99.     )
    Vpt     = RooRealVar( "V.Pt()",           "",           -1.,   1.e6     )
    CosThetaStar = RooRealVar( "CosThetaStar","",          -99.,    99.     )
    CosTheta1 = RooRealVar( "CosTheta1",      "",          -99.,    99.     )
    TopVeto = RooRealVar( "isTveto",          "",            0.,     2.     )
    isZtoNN = RooRealVar( "isZtoNN",          "",            0.,     2.     )
    isWtoEN = RooRealVar( "isWtoEN",          "",            0.,     2.     )
    isWtoMN = RooRealVar( "isWtoMN",          "",            0.,     2.     )
    isZtoEE = RooRealVar( "isZtoEE",          "",            0.,     2.     )
    isZtoMM = RooRealVar( "isZtoMM",          "",            0.,     2.     )
    isVtoQQ = RooRealVar( "isVtoQQ",          "",            0.,     2.     )
    weight  = RooRealVar( "eventWeightLumi",  "",         -1.e9,   1.e9     )

    if isAH:
        Xmin = 985
        Xmax = Xmin + 4100
    else:
        Xmin = 750
        Xmax = Xmin + 4000

#    X_mass.setMin(Xmin)
#    X_mass.setMax(Xmax)

#    if isAH:
#        X_mass.setMin(950)
#        X_mass.setMax(4950)
#        if channel.endswith('lpb'):
#            X_mass.setMin(975)
#            X_mass.setMax(5075)

    # Define the RooArgSet which will include all the variables defined before
    # there is a maximum of 9 variables in the declaration, so the others need to be added with 'add'
    variables = RooArgSet(X_mass, J_mass, V_mass, CSV1, CSV2, H_ntag, H_dbt, H_tau21, V_tau21)
    variables.add(RooArgSet(DEta, MaxBTag, MinDPhi, nTaus, CosThetaStar, CosTheta1, Vpt))
    variables.add(RooArgSet(TopVeto, isZtoNN, isWtoEN, isWtoMN, isZtoEE, isZtoMM, isVtoQQ, weight))
    #X_mass.setRange("X_extended_range", X_mass.getMin(), X_mass.getMax())
    X_mass.setRange("X_reasonable_range", X_mass.getMin(), X_mass.getMax())
    X_mass.setRange("X_integration_range", Xmin, Xmax)
    X_mass.setBins(int((X_mass.getMax() - X_mass.getMin())/100))
    binsXmass = RooBinning(int((X_mass.getMax() - X_mass.getMin())/100), X_mass.getMin(), X_mass.getMax())
    X_mass.setBinning(binsXmass, "PLOT")
    massArg = RooArgSet(X_mass)

    # Cuts
    SRcut = selection[category]+selection['SR'] #+ " && %s>%d && %s<%d" % (J_mass.GetName(), SIGMIN, J_mass.GetName(), SIGMAX)
    print "  Cut:\t", SRcut
    #SRcut = SRcut.replace('isVtoQQ', '0==0')

    #*******************************************************#
    #                                                       #
    #                    Signal fits                        #
    #                                                       #
    #*******************************************************#

    treeSign = {}
    setSignal = {}

    vmean  = {}
    vsigma = {}
    valpha1 = {}
    vslope1 = {}
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
    smean_fit = RooRealVar("CMS2016_sig_p1_fit", "Change of the resonance position with the fit uncertainty", 0., -10, 10)
    xmean_jes = RooRealVar("sig_p1_scale_jes", "Variation of the resonance position with the jet energy scale", 0.020 if isAH else 0.010, -1., 1.) #0.001
    smean_jes = RooRealVar("CMS2016_sig_p1_jes", "Change of the resonance position with the jet energy scale", 0., -10, 10)
    xmean_e = RooRealVar("sig_p1_scale_e", "Variation of the resonance position with the electron energy scale", 0.001, -1., 1.)
    smean_e = RooRealVar("CMS2016_sig_p1_scale_e", "Change of the resonance position with the electron energy scale", 0., -10, 10)
    xmean_m = RooRealVar("sig_p1_scale_m", "Variation of the resonance position with the muon energy scale", 0.001, -1., 1.)
    smean_m = RooRealVar("CMS2016_sig_p1_scale_m", "Change of the resonance position with the muon energy scale", 0., -10, 10)

    xsigma_fit = RooRealVar("sig_p2_fit", "Variation of the resonance width with the fit uncertainty", 0.02, -1., 1.)
    ssigma_fit = RooRealVar("CMS2016_sig_p2_fit", "Change of the resonance width with the fit uncertainty", 0., -10, 10)
    xsigma_jes = RooRealVar("sig_p2_scale_jes", "Variation of the resonance width with the jet energy scale", 0.010, -1., 1.) #0.001
    ssigma_jes = RooRealVar("CMS2016_sig_p2_jes", "Change of the resonance width with the jet energy scale", 0., -10, 10)
    xsigma_jer = RooRealVar("sig_p2_scale_jer", "Variation of the resonance width with the jet energy resolution", 0.020, -1., 1.)
    ssigma_jer = RooRealVar("CMS2016_sig_p2_jer", "Change of the resonance width with the jet energy resolution", 0., -10, 10)
    xsigma_e = RooRealVar("sig_p2_scale_e", "Variation of the resonance width with the electron energy scale", 0.001, -1., 1.)
    ssigma_e = RooRealVar("CMS2016_sig_p2_scale_e", "Change of the resonance width with the electron energy scale", 0., -10, 10)
    xsigma_m = RooRealVar("sig_p2_scale_m", "Variation of the resonance width with the muon energy scale", 0.040, -1., 1.)
    ssigma_m = RooRealVar("CMS2016_sig_p2_scale_m", "Change of the resonance width with the muon energy scale", 0., -10, 10)
    
    xalpha1_fit = RooRealVar("sig_p3_fit", "Variation of the resonance alpha with the fit uncertainty", 0.03, -1., 1.)
    salpha1_fit = RooRealVar("CMS2016_sig_p3_fit", "Change of the resonance alpha with the fit uncertainty", 0., -10, 10)
    
    xslope1_fit = RooRealVar("sig_p4_fit", "Variation of the resonance slope with the fit uncertainty", 0.10, -1., 1.)
    sslope1_fit = RooRealVar("CMS2016_sig_p4_fit", "Change of the resonance slope with the fit uncertainty", 0., -10, 10)

    xmean_fit.setConstant(True)
    smean_fit.setConstant(True)
    xmean_jes.setConstant(True)
    smean_jes.setConstant(True)
    xmean_e.setConstant(True)
    smean_e.setConstant(True)
    xmean_m.setConstant(True)
    smean_m.setConstant(True)
    
    xsigma_fit.setConstant(True)
    ssigma_fit.setConstant(True)
    xsigma_jes.setConstant(True)
    ssigma_jes.setConstant(True)
    xsigma_jer.setConstant(True)
    ssigma_jer.setConstant(True)
    xsigma_e.setConstant(True)
    ssigma_e.setConstant(True)
    xsigma_m.setConstant(True)
    ssigma_m.setConstant(True)
    
    xalpha1_fit.setConstant(True)
    salpha1_fit.setConstant(True)
    xslope1_fit.setConstant(True)
    sslope1_fit.setConstant(True)

    # Assign shape uncertainties
    #if isAH:
    #    xmean_jes.setVal(0.015)
    #    xsigma_jer.setVal(0.030)


    # the alpha method is now done.
    for m in massPoints:

        if isAH and m < 1000: continue
        #if not isAH and m > 4000: continue
        #if 'nn' in channel and m==1000: continue
        #if m==1600 or m==2000: continue

        signalString = "M%d" % m
        signalMass = "%s_M%d" % (stype, m)
        signalName = "%s%s_M%d" % (stype, category, m)
        
        signalColor = sample[signalName]['linecolor'] if signalName in sample else 1
        # fit the shape of the signal and put everything together in the datacard and workspace
        # for the time being the signal is fitted using 1 Gaussian in a range defined below (hardcoded)

        # define the signal PDF
        vmean[m] = RooRealVar(signalName + "_vmean", "Crystal Ball mean", m, m*0.5, m*1.25)
        #smean[m] = RooFormulaVar(signalName + "_mean", "@0*(@1*@2*@3)", RooArgList(vmean[m], smean_e, smean_m, smean_jes))
        smean[m] = RooFormulaVar(signalName + "_mean", "@0*(1+@1*@2)*(1+@3*@4)*(1+@5*@6)*(1+@7*@8)", RooArgList(vmean[m], xmean_e, smean_e, xmean_m, smean_m, xmean_jes, smean_jes, xmean_fit, smean_fit))

        vsigma[m] = RooRealVar(signalName + "_vsigma", "Crystal Ball sigma", m*0.035, m*0.01, m*0.4)
        #ssigma[m] = RooFormulaVar(signalName + "_sigma", "@0*(@1*@2*@3*@4)", RooArgList(vsigma[m], ssigma_e, ssigma_e, ssigma_jes, ssigma_jer))
        sigmaList = RooArgList(vsigma[m], xsigma_e, ssigma_e, xsigma_m, ssigma_m, xsigma_jes, ssigma_jes, xsigma_jer, ssigma_jer)
        sigmaList.add(RooArgList(xsigma_fit, ssigma_fit))
        ssigma[m] = RooFormulaVar(signalName + "_sigma", "@0*(1+@1*@2)*(1+@3*@4)*(1+@5*@6)*(1+@7*@8)*(1+@9*@10)", sigmaList)
        
        valpha1[m] = RooRealVar(signalName + "_valpha1", "Crystal Ball alpha", 1.,  0., 5.) # number of sigmas where the exp is attached to the gaussian core. >0 left, <0 right
        salpha1[m] = RooFormulaVar(signalName + "_alpha1", "@0*(1+@1*@2)", RooArgList(valpha1[m], xalpha1_fit, salpha1_fit))

        vslope1[m] = RooRealVar(signalName + "_vslope1", "Crystal Ball slope", 10., 1., 60.) # slope of the power tail
        sslope1[m] = RooFormulaVar(signalName + "_slope1", "@0*(1+@1*@2)", RooArgList(vslope1[m], xslope1_fit, sslope1_fit))

#        smean[m] = RooRealVar(signalName + "_mean" , "mean of the Crystal Ball", m, m*0.8, m*1.2)
#        ssigma[m] = RooRealVar(signalName + "_sigma", "Crystal Ball sigma", m*0.04, m*0.001, m*0.2)
#        salpha1[m] = RooRealVar(signalName + "_alpha1", "Crystal Ball alpha", 1,  0., 5.) # number of sigmas where the exp is attached to the gaussian core. >0 left, <0 right
#        sslope1[m] = RooRealVar(signalName + "_slope1", "Crystal Ball slope", 20, 10., 60.) # slope of the power tail
        salpha2[m] = RooRealVar(signalName + "_alpha2", "Crystal Ball alpha", 2,  1., 5.) # number of sigmas where the exp is attached to the gaussian core. >0 left, <0 right
        sslope2[m] = RooRealVar(signalName + "_slope2", "Crystal Ball slope", 10, 1.e-1, 115.) # slope of the power tail
#        if isAH: signal[m] = RooDoubleCrystalBall(signalString, "Double Crystal Ball", X_mass, smean[m], ssigma[m], salpha1[m], sslope1[m], salpha2[m], sslope2[m]) # Signal name does not have the channel
#        else:
        signal[m] = RooCBShape(signalName, "m_{%s'} = %d GeV" % (stype[1], m), X_mass, smean[m], ssigma[m], salpha1[m], sslope1[m]) # Signal name does not have the channel
#        if 'nn' in channel and m<1000: signal[m] = RooGaussian(signalName, "m_{%s'} = %d GeV" % (stype[1], m), X_mass, smean[m], ssigma[m])

        # extend the PDF with the yield to perform an extended likelihood fit
        signalYield[m] = RooRealVar(signalName+"_yield", "signalYield", 100, 0., 1.e6)
        signalNorm[m] = RooRealVar(signalName+"_norm", "signalNorm", 1., 0., 1.e6)
        signalXS[m] = RooRealVar(signalName+"_xs", "signalXS", 1., 0., 1.e6)
        signalExt[m] = RooExtendPdf(signalName+"_ext", "extended p.d.f", signal[m], signalYield[m])

        if 'nn' in channel:
            if m<1000.: valpha1[m].setConstant(True)
            else: valpha1[m].setVal(0.5)
            vmean[m].setVal(m*0.9)
            vsigma[m].setVal(m*0.08)
#            vslope1[m].setVal(40.)
#            salpha1[m].setVal(5.)
#            sslope1[m].setConstant(True)
#            sslope1[m].setVal(100.)
        else:
            vslope1[m].setMax(40.)

        if m < 1000: vsigma[m].setVal(m*0.06)

        # If it's not the proper channel, make it a gaussian
        if not isAH and ((nLept==1 and stype=='XZH') or (nLept!=1 and stype=='XWH')):
            valpha1[m].setVal(5)
            valpha1[m].setConstant(True)
            vslope1[m].setConstant(True)
            salpha2[m].setConstant(True)
            sslope2[m].setConstant(True)

        
        # ---------- if there is no simulated signal, skip this mass point ----------
        if m in genPoints:
            if VERBOSE: print " - Mass point", m
    #        if stype=='XZH' and (m==1200 or m==2000 or m==4000): continue
    #        if stype=='XWH' and m==4000: continue
    #        if stype=='XVH' and (m==1200 or m==2000 or m==4000): continue
    #        badFiles = []
    #        for j, ss in enumerate(sample[signalMass]['files']):
    #            if not 'had' in ss: continue
    #            tmpFile = TFile(NTUPLEDIR + ss + ".root", "R")
    #            tmpHist = tmpFile.Get("Events")
    #            if not tmpHist==None: badFiles.append(ss)
    #        if len(badFiles) > 0:
    #            print "WARNING: mass point", m, "samples are incomplete:", badFiles
    #            continue

            # define the dataset for the signal applying the SR cuts
            treeSign[m] = TChain("tree")
            for j, ss in enumerate(sample[signalMass]['files']):
    #            if isAH and ('lep' in ss or 'inv' in ss): continue
    #            if not isAH and 'had' in ss: continue
                treeSign[m].Add(NTUPLEDIR + ss + ".root")
            
            if treeSign[m].GetEntries() <= 0.:
                if VERBOSE: print " - 0 events available for mass", m, "skipping mass point..."
                signalNorm[m].setVal(-1)
                vmean[m].setConstant(True)
                vsigma[m].setConstant(True)
                salpha1[m].setConstant(True)
                sslope1[m].setConstant(True)
                salpha2[m].setConstant(True)
                sslope2[m].setConstant(True)
                signalNorm[m].setConstant(True)
                signalXS[m].setConstant(True)
                continue
            
            setSignal[m] = RooDataSet("setSignal_"+signalName, "setSignal", variables, RooFit.Cut(SRcut), RooFit.WeightVar(weight), RooFit.Import(treeSign[m]))
            if VERBOSE: print " - Dataset with", setSignal[m].sumEntries(), "events loaded"
            
            # FIT
            signalYield[m].setVal(setSignal[m].sumEntries())
            
            if treeSign[m].GetEntries(SRcut) > 5:
                if VERBOSE: print " - Running fit"
        #        # Step 1: fit gaussian first
        #        salpha1[m].setConstant(True)
        #        sslope1[m].setConstant(True)
        #        salpha2[m].setConstant(True)
        #        sslope2[m].setConstant(True)
        #        frSignal1[m] = signalExt[m].fitTo(setSignal[m], RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.Extended(True), RooFit.SumW2Error(True), RooFit.PrintLevel(1 if VERBOSE else -1))
        #
        #        # Step 2: fit lower tails
        #        signalYield[m].setConstant(True)
        #        smean[m].setConstant(True)
        #        ssigma[m].setConstant(True)
        #        salpha1[m].setConstant(False)
        #        sslope1[m].setConstant(False)
        #        frSignal2[m] = signalExt[m].fitTo(setSignal[m], RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.Extended(False), RooFit.SumW2Error(True), RooFit.PrintLevel(1 if VERBOSE else -1))
        #
        #        # Step 2: fit lower tails
        #        salpha1[m].setConstant(True)
        #        sslope1[m].setConstant(True)
        #        salpha2[m].setConstant(False)
        #        sslope2[m].setConstant(False)
        #        frSignal3[m] = signalExt[m].fitTo(setSignal[m], RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.Extended(False), RooFit.SumW2Error(True), RooFit.PrintLevel(1 if VERBOSE else -1))
        #
        #        # Step 4: refit everything together
        #        signalYield[m].setConstant(False)
        #        smean[m].setConstant(False)
        #        ssigma[m].setConstant(False)
        #        salpha1[m].setConstant(False)
        #        sslope1[m].setConstant(False)
        #        salpha2[m].setConstant(False)
        #        sslope2[m].setConstant(False)

        #        gaussian.fitTo(setSignal[m], RooFit.Strategy(0), RooFit.Minimizer("Minuit"), RooFit.Save(0), RooFit.Extended(True), RooFit.SumW2Error(True), RooFit.PrintLevel(1 if VERBOSE else -1))
        #        signalYield[m].setConstant(True)
#                frSignal[m] = signalExt[m].fitTo(setSignal[m], RooFit.Strategy(0), RooFit.Minimizer("Minuit"), RooFit.Save(1), RooFit.Extended(True), RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
                frSignal[m] = signalExt[m].fitTo(setSignal[m], RooFit.Save(1), RooFit.Extended(True), RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
                if VERBOSE: print "********** Fit result [", m, "] **", category, "*"*40, "\n", frSignal[m].Print(), "\n", "*"*80
                if VERBOSE: frSignal[m].correlationMatrix().Print()
                #, RooFit.Range("X_reasonable_range")
        #        , RooFit.Strategy(2), RooFit.Minimizer("Minuit2")
        #        , RooFit.Range(0, 5000)
        #        , RooFit.Save(1)

        ###        # Refit the tail
        ###        #if 'nn' in channel:
        ###        #    sslope1[m].setMax(40)
        ###        vmean[m].setConstant(True)
        ###        vsigma[m].setConstant(True)
        ###        salpha1[m].setConstant(True)
        ###        signal[m].fitTo(setSignal[m], RooFit.Strategy(0), RooFit.Minimizer("Minuit"), RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
        ###        salpha1[m].setConstant(False)
        ###        sslope1[m].setConstant(True)
        ###        signal[m].fitTo(setSignal[m], RooFit.Strategy(0), RooFit.Minimizer("Minuit"), RooFit.SumW2Error(True), RooFit.PrintLevel(-1))
        ###        salpha1[m].setConstant(True)
        ###        vmean[m].setConstant(False)
        ###        vsigma[m].setConstant(False)
        ###        frSignal[m] = signalExt[m].fitTo(setSignal[m], RooFit.Strategy(0), RooFit.Minimizer("Minuit"), RooFit.Save(1), RooFit.Extended(True), RooFit.SumW2Error(True), RooFit.PrintLevel(1 if VERBOSE else -1))

                

                #if m==3500: ssigma[m].setVal(250.)
        #        smean[m].setConstant(True)
        #        ssigma[m].setConstant(True)
        #        salpha[m].setConstant(True)
        #        sslope[m].setConstant(True)
                #massset = RooArgSet(X_mass)

                #print signalName, signalNorm[m].getVal(), setSignal[m].sumEntries(), signal[m].createIntegral(massset, RooFit.NormSet(massset)).getVal()
                drawPlot(signalMass, stype+channel, X_mass, signal[m], setSignal[m], frSignal[m])
            
            else:
                print "  WARNING: signal", stype, "and mass point", m, "in channel", channel, "has 0 entries or does not exist"
                        
            # Remove HVT cross sections
            xs = getCrossSection(stype, channel, m)
            #if isAH: xs /= 0.6991 #FIXME
            signalXS[m].setVal(xs * 1000.)
            
            signalIntegral[m] = signalExt[m].createIntegral(massArg, RooFit.NormSet(massArg), RooFit.Range("X_integration_range"))
            boundaryFactor = signalIntegral[m].getVal()
            if VERBOSE: print " - Fit normalization vs integral:", signalYield[m].getVal(), "/", boundaryFactor, "events"
            signalNorm[m].setVal( boundaryFactor * signalYield[m].getVal() / signalXS[m].getVal()) # here normalize to sigma(X) x Br(X->VH) = 1 [fb]

            # Apply V-tagging scale factors
            if isAH:
                if isHP: signalNorm[m].setVal( signalNorm[m].getVal() * 0.99 ) #0.99 +- 0.11
                if isLP: signalNorm[m].setVal( signalNorm[m].getVal() * 1.03 ) #1.03 +- 0.23



        vmean[m].setConstant(True)
        vsigma[m].setConstant(True)
        valpha1[m].setConstant(True)
        vslope1[m].setConstant(True)
        salpha2[m].setConstant(True)
        sslope2[m].setConstant(True)
        signalNorm[m].setConstant(True)
        signalXS[m].setConstant(True)

        # Fast dump if interpolation is not needed
        if signalType=='monoH':
            w = RooWorkspace("VH_2016", "workspace")
            getattr(w, "import")(signal[m], RooFit.Rename(signal[m].GetName()))
            getattr(w, "import")(signalNorm[m], RooFit.Rename(signalNorm[m].GetName()))
            getattr(w, "import")(signalXS[m], RooFit.Rename(signalXS[m].GetName()))
            w.writeToFile("%s%s.root" % (WORKDIR, signalName), True)
            print "Workspace", "%s%s.root" % (WORKDIR, signalName), "saved successfully"

    if signalType=='monoH': return

    #*******************************************************#
    #                                                       #
    #                 Signal interpolation                  #
    #                                                       #
    #*******************************************************#


    # ====== CONTROL PLOT ======
    c_signal = TCanvas("c_signal", "c_signal", 800, 600)
    c_signal.cd()
    frame_signal = X_mass.frame()
    for m in genPoints:
        if m in signalExt.keys():
            signal[m].plotOn(frame_signal, RooFit.LineColor(sample["%s_M%d" % (stype, m)]['linecolor']), RooFit.Normalization(signalNorm[m].getVal(), RooAbsReal.NumEvent), RooFit.Range("X_reasonable_range"))
    frame_signal.GetXaxis().SetRangeUser(0, 5000)
    frame_signal.Draw()
    drawCMS(-1, "Simulation")
    drawAnalysis(channel)
    drawRegion(channel)
    c_signal.SaveAs(PLOTDIR+"/"+stype+category+"/"+stype+"_Signal.pdf")
    c_signal.SaveAs(PLOTDIR+"/"+stype+category+"/"+stype+"_Signal.png")
    if VERBOSE: raw_input("Press Enter to continue...")
    # ====== CONTROL PLOT ======



    #ffile = TFile("workspaces/"+channel+".root", "READ")
    #w = ffile.Get("Vh_2015")
    #w.Print()

    # Normalization
    gnorm = TGraphErrors()
    gnorm.SetTitle(";m_{X} (GeV);integral (GeV)")
    gnorm.SetMarkerStyle(20)
    gnorm.SetMarkerColor(1)
    gnorm.SetMaximum(0)
    inorm = TGraphErrors()
    inorm.SetMarkerStyle(24)
#    if not HVTMODEL:
    fnorm = TF1("fnorm", "pol3" if isAH else "pol9", 700, 3000) #"pol5" if not channel=="XZHnnbb" else "pol6" #pol5*TMath::Floor(x-1800) + ([5]*x + [6]*x*x)*(1-TMath::Floor(x-1800))
#    else:
#        fnorm = TF1("fnorm", "(%e + %e*x + %e*x*x + %e*x*x*x + %e*x*x*x*x + %e*x*x*x*x*x)*[0]*exp(x*[1] + [2]/x)" % (param[channel]['norm'][0], param[channel]['norm'][1], param[channel]['norm'][2], param[channel]['norm'][3], param[channel]['norm'][4], param[channel]['norm'][5]), 750, 5000)
##        fnorm = TF1("fnorm", "pol5 * expo", 750, 4000)
#        fnorm.SetParameter(0, 0.55)
#        #fnorm.FixParameter(0, 1)
#        fnorm.SetParameter(1, -2.2e-3)
#        fnorm.SetParameter(2, 1200)
#        fnorm.SetParLimits(2, 800, 2000)
#        #fnorm.FixParameter(2, 1200)
#        #fnorm.FixParameter(3, 8000)
    fnorm.SetLineColor(920)
    fnorm.SetLineStyle(7)
    fnorm.SetFillColor(2)
    fnorm.SetLineColor(cColor)

    # Mean
    gmean = TGraphErrors()
    gmean.SetTitle(";m_{X} (GeV);gaussian mean (GeV)")
    gmean.SetMarkerStyle(20)
    gmean.SetMarkerColor(cColor)
    gmean.SetLineColor(cColor)
    imean = TGraphErrors()
    imean.SetMarkerStyle(24)
    fmean = TF1("fmean", "pol1", 0, 5000)
    fmean.SetLineColor(2)
    fmean.SetFillColor(2)

    # Width
    gsigma = TGraphErrors()
    gsigma.SetTitle(";m_{X} (GeV);gaussian width (GeV)")
    gsigma.SetMarkerStyle(20)
    gsigma.SetMarkerColor(cColor)
    gsigma.SetLineColor(cColor)
    isigma = TGraphErrors()
    isigma.SetMarkerStyle(24)
    fsigma = TF1("fsigma", "pol1", 0, 5000)
    fsigma.SetLineColor(2)
    fsigma.SetFillColor(2)

    # Alpha1
    galpha1 = TGraphErrors()
    galpha1.SetTitle(";m_{X} (GeV);crystal ball lower alpha")
    galpha1.SetMarkerStyle(20)
    galpha1.SetMarkerColor(cColor)
    galpha1.SetLineColor(cColor)
    ialpha1 = TGraphErrors()
    ialpha1.SetMarkerStyle(24)
    falpha1 = TF1("falpha", "pol0", 0, 5000)
    falpha1.SetLineColor(2)
    falpha1.SetFillColor(2)

    # Slope1
    gslope1 = TGraphErrors()
    gslope1.SetTitle(";m_{X} (GeV);exponential lower slope (1/Gev)")
    gslope1.SetMarkerStyle(20)
    gslope1.SetMarkerColor(cColor)
    gslope1.SetLineColor(cColor)
    islope1 = TGraphErrors()
    islope1.SetMarkerStyle(24)
    fslope1 = TF1("fslope", "pol0", 0, 5000)
    fslope1.SetLineColor(2)
    fslope1.SetFillColor(2)

    # Alpha2
    galpha2 = TGraphErrors()
    galpha2.SetTitle(";m_{X} (GeV);crystal ball upper alpha")
    galpha2.SetMarkerStyle(20)
    galpha2.SetMarkerColor(cColor)
    galpha2.SetLineColor(cColor)
    ialpha2 = TGraphErrors()
    ialpha2.SetMarkerStyle(24)
    falpha2 = TF1("falpha", "pol0", 0, 5000)
    falpha2.SetLineColor(2)
    falpha2.SetFillColor(2)

    # Slope2
    gslope2 = TGraphErrors()
    gslope2.SetTitle(";m_{X} (GeV);exponential upper slope (1/Gev)")
    gslope2.SetMarkerStyle(20)
    gslope2.SetMarkerColor(cColor)
    gslope2.SetLineColor(cColor)
    islope2 = TGraphErrors()
    islope2.SetMarkerStyle(24)
    fslope2 = TF1("fslope", "pol0", 0, 5000)
    fslope2.SetLineColor(2)
    fslope2.SetFillColor(2)



    n = 0
    for i, m in enumerate(genPoints):
        if not m in signalNorm.keys(): continue
        #if not signalNorm[m].getVal() > 1.: continue
        if signalNorm[m].getVal() < 1.e-6: continue
        signalString = "M%d" % m
        signalName = "%s_M%d" % (stype, m)

        if gnorm.GetMaximum() < signalNorm[m].getVal(): gnorm.SetMaximum(signalNorm[m].getVal())
        gnorm.SetPoint(n, m, signalNorm[m].getVal())
        #gnorm.SetPointError(i, 0, signalNorm[m].getVal()/math.sqrt(treeSign[m].GetEntriesFast()))
        gmean.SetPoint(n, m, vmean[m].getVal())
        gmean.SetPointError(n, 0, min(vmean[m].getError(), vmean[m].getVal()*0.02))
        gsigma.SetPoint(n, m, vsigma[m].getVal())
        gsigma.SetPointError(n, 0, min(vsigma[m].getError(), vsigma[m].getVal()*0.05))
        galpha1.SetPoint(n, m, valpha1[m].getVal())
        galpha1.SetPointError(n, 0, min(valpha1[m].getError(), valpha1[m].getVal()*0.10))
        gslope1.SetPoint(n, m, vslope1[m].getVal())
        gslope1.SetPointError(n, 0, min(vslope1[m].getError(), vslope1[m].getVal()*0.10))
        galpha2.SetPoint(n, m, salpha2[m].getVal())
        galpha2.SetPointError(n, 0, min(salpha2[m].getError(), salpha2[m].getVal()*0.10))
        gslope2.SetPoint(n, m, sslope2[m].getVal())
        gslope2.SetPointError(n, 0, min(sslope2[m].getError(), sslope2[m].getVal()*0.10))
        #tmpVar = w.var(var+"_"+signalString)
        #print m, tmpVar.getVal(), tmpVar.getError()
        n = n + 1

    gmean.Fit(fmean, "Q0", "SAME")
    gsigma.Fit(fsigma, "Q0", "SAME")
    galpha1.Fit(falpha1, "Q0", "SAME")
    gslope1.Fit(fslope1, "Q0", "SAME")
    galpha2.Fit(falpha2, "Q0", "SAME")
    gslope2.Fit(fslope2, "Q0", "SAME")
#    gnorm.Fit(fnorm, "Q0", "", 700, 5000)
    for m in [5000, 5500]: gnorm.SetPoint(gnorm.GetN(), m, gnorm.Eval(m, 0, "S"))
    gnorm.Fit(fnorm, "Q", "SAME", 700, 6000)

    for m in massPoints:
        if isAH and m < 1000: continue

        signalName = "%s_M%d" % (stype, m)

        # set parameters
        # Fit method
#        vmean[m].setVal(fmean.GetParameter(0) + fmean.GetParameter(1)*m + fmean.GetParameter(2)*m*m)
#        vsigma[m].setVal(fsigma.GetParameter(0) + fsigma.GetParameter(1)*m + fsigma.GetParameter(2)*m*m)
#        valpha1[m].setVal(falpha1.GetParameter(0) + falpha1.GetParameter(1)*m + falpha1.GetParameter(2)*m*m)
#        vslope1[m].setVal(fslope1.GetParameter(0) + fslope1.GetParameter(1)*m + fslope1.GetParameter(2)*m*m)
#        salpha2[m].setVal(falpha2.GetParameter(0) + falpha2.GetParameter(1)*m + falpha2.GetParameter(2)*m*m)
#        sslope2[m].setVal(fslope2.GetParameter(0) + fslope2.GetParameter(1)*m + fslope2.GetParameter(2)*m*m)

        if vsigma[m].getVal() < 10.: vsigma[m].setVal(10.)

        # Interpolation method
        syield = gnorm.Eval(m)
        spline = gnorm.Eval(m, 0, "S")
        sfunct = fnorm.Eval(m)
        if isAH:
            if m < 1200: syield = max(spline, syield)
            if stype=='XZH' and m==1100: syield *= 1.30
        
        #delta = min(abs(1.-spline/sfunct), abs(1.-spline/syield))
        delta = abs(1.-spline/sfunct) if sfunct > 0 else 0
        syield = spline
        
        #if isAH:
            #syield = max(gnorm.Eval(m, 0, "S"), syield)
#            if m < 1200 or m > 3500:
            #syield = max(syield, fnorm.Eval(m)) #FIXME
            # #FIXME
        
        if interPar:
            jmean = gmean.Eval(m)
            jsigma = gsigma.Eval(m)
            jalpha1 = galpha1.Eval(m)
            jslope1 = gslope1.Eval(m)
        else:
            jmean = fmean.GetParameter(0) + fmean.GetParameter(1)*m + fmean.GetParameter(2)*m*m
            jsigma = fsigma.GetParameter(0) + fsigma.GetParameter(1)*m + fsigma.GetParameter(2)*m*m
            jalpha1 = falpha1.GetParameter(0) + falpha1.GetParameter(1)*m + falpha1.GetParameter(2)*m*m
            jslope1 = fslope1.GetParameter(0) + fslope1.GetParameter(1)*m + fslope1.GetParameter(2)*m*m

        inorm.SetPoint(inorm.GetN(), m, syield)
        signalNorm[m].setVal(syield)

        imean.SetPoint(imean.GetN(), m, jmean)
        if jmean > 0: vmean[m].setVal(jmean)

        isigma.SetPoint(isigma.GetN(), m, jsigma)
        if jsigma > 0: vsigma[m].setVal(jsigma)

        ialpha1.SetPoint(ialpha1.GetN(), m, jalpha1)
        if not jalpha1==0: valpha1[m].setVal(jalpha1)

        islope1.SetPoint(islope1.GetN(), m, jslope1)
        if jslope1 > 0: vslope1[m].setVal(jslope1)
    

    c1 = TCanvas("c1", "Crystal Ball", 1200, 800) #if not isAH else 1200
    c1.Divide(2, 2) # if not isAH else 3
    c1.cd(1)
    gmean.SetMinimum(0.)
    gmean.Draw("APL")
    imean.Draw("P, SAME")
    drawRegion(channel)
#    emean = TGraphErrors(gmean)
#    emean.SetFillStyle(3003)
#    emean.SetFillColor(1)
#    if emean.GetN() > 0: TVirtualFitter.GetFitter().GetConfidenceIntervals(emean, 0.683)
#    emean.Draw("3, SAME")
    c1.cd(2)
    gsigma.SetMinimum(0.)
    gsigma.Draw("APL")
    isigma.Draw("P, SAME")
    drawRegion(channel)
#    esigma = TGraphErrors(gsigma)
#    esigma.SetFillStyle(3003)
#    esigma.SetFillColor(1)
#    if esigma.GetN() > 0: TVirtualFitter.GetFitter().GetConfidenceIntervals(esigma, 0.683)
#    esigma.Draw("3, SAME")
    c1.cd(3)
    galpha1.Draw("APL")
    ialpha1.Draw("P, SAME")
    drawRegion(channel)
    galpha1.GetYaxis().SetRangeUser(0., 5.)
    #falpha1.FixParameter(0, 0.)
#    ealpha1 = TGraphErrors(galpha1)
#    ealpha1.SetFillStyle(3003)
#    ealpha1.SetFillColor(1)
#    if ealpha1.GetN() > 0: TVirtualFitter.GetFitter().GetConfidenceIntervals(ealpha1, 0.683)
#    ealpha1.Draw("3, SAME")
    c1.cd(4)
    gslope1.Draw("APL")
    islope1.Draw("P, SAME")
    drawRegion(channel)
    gslope1.GetYaxis().SetRangeUser(0., 125.)
#    eslope1 = TGraphErrors(gslope1)
#    eslope1.SetFillStyle(3003)
#    eslope1.SetFillColor(1)
#    if eslope1.GetN() > 0: TVirtualFitter.GetFitter().GetConfidenceIntervals(eslope1, 0.683)
#    eslope1.Draw("3, SAME")
    if False: #isAH:
        c1.cd(5)
        galpha2.Draw("APL")
        ialpha2.Draw("P, SAME")
        drawRegion(channel)
        #falpha2.FixParameter(0, 0.)
#        galpha2.GetYaxis().SetRangeUser(0., 6.)
#        ealpha2 = TGraphErrors(galpha2)
#        ealpha2.SetFillStyle(3003)
#        ealpha2.SetFillColor(1)
#        if ealpha2.GetN() > 0: TVirtualFitter.GetFitter().GetConfidenceIntervals(ealpha2, 0.683)
#        ealpha2.Draw("3, SAME")
        c1.cd(6)
        gslope2.Draw("APL")
        islope2.Draw("P, SAME")
        drawRegion(channel)
        gslope2.GetYaxis().SetRangeUser(0., 10.)
#        eslope2 = TGraphErrors(gslope2)
#        eslope2.SetFillStyle(3003)
#        eslope2.SetFillColor(1)
#        if eslope2.GetN() > 0: TVirtualFitter.GetFitter().GetConfidenceIntervals(eslope2, 0.683)
#        eslope2.Draw("3, SAME")


    c1.Print(PLOTDIR+stype+category+"/"+stype+"_SignalShape.pdf")
    c1.Print(PLOTDIR+stype+category+"/"+stype+"_SignalShape.png")


    c2 = TCanvas("c2", "Signal Efficiency", 800, 600)
    c2.cd(1)
    gnorm.SetMarkerColor(cColor)
    gnorm.SetMarkerStyle(20)
    gnorm.SetLineColor(cColor)
    gnorm.SetLineWidth(2)
    gnorm.Draw("APL")
    inorm.Draw("P, SAME")
    gnorm.GetXaxis().SetRangeUser(genPoints[0]-100, genPoints[-1]+100)
    gnorm.GetYaxis().SetRangeUser(0., gnorm.GetMaximum()*1.25)
    drawCMS(-1, "Simulation")
    drawAnalysis(channel)
    drawRegion(channel)
    c2.Print(PLOTDIR+stype+category+"/"+stype+"_SignalNorm.pdf")
    c2.Print(PLOTDIR+stype+category+"/"+stype+"_SignalNorm.png")


    #*******************************************************#
    #                                                       #
    #                       Signal pdf                      #
    #                                                       #
    #*******************************************************#

#    X_mass.setMin(Xmin)
#    X_mass.setMax(Xmax)




    #*******************************************************#
    #                                                       #
    #                   Generate workspace                  #
    #                                                       #
    #*******************************************************#

#    from ROOT import RooMultiPdf
#    cat = RooCategory("pdf_index", "Index of Pdf which is active");
#    pdfs = RooArgList(modelBkg, modelAlt)
#    roomultipdf = RooMultiPdf("roomultipdf", "All Pdfs", cat, pdfs)
#    norm = RooRealVar("roomultipdf_norm", "Number of background events", nevents, 0., 1.e6)
#    norm = RooRealVar(modelBkg.GetName()+"_norm", "Number of background events", nevents, 0., 1.e10)

    # create workspace
    w = RooWorkspace("VH_2016", "workspace")
    for m in massPoints:
        if isAH and m < 1000: continue
        getattr(w, "import")(signal[m], RooFit.Rename(signal[m].GetName()))
        getattr(w, "import")(signalNorm[m], RooFit.Rename(signalNorm[m].GetName()))
        getattr(w, "import")(signalXS[m], RooFit.Rename(signalXS[m].GetName()))
    w.writeToFile("%s%s.root" % (WORKDIR, stype+channel), True)
    print "Workspace", "%s%s.root" % (WORKDIR, stype+channel), "saved successfully"
    #w.Print()

    #param = pickle.load( open( SIGNALFILE, "rb" ) )
    #param[channel] = {'mean' : [fmean.GetParameter(0), fmean.GetParameter(1)], 'sigma' : [fsigma.GetParameter(0), fsigma.GetParameter(1)], 'alpha1' : [falpha1.GetParameter(0), falpha1.GetParameter(1)], 'slope1' : [fslope1.GetParameter(0), fslope1.GetParameter(1)], 'alpha2' : [falpha2.GetParameter(0), falpha2.GetParameter(1)], 'slope2' : [fslope2.GetParameter(0), fslope2.GetParameter(1)], 'norm' : [fnorm.GetParameter(0), fnorm.GetParameter(1), fnorm.GetParameter(2), fnorm.GetParameter(3), fnorm.GetParameter(4), fnorm.GetParameter(5), fnorm.GetParameter(6), fnorm.GetParameter(7), fnorm.GetParameter(8), fnorm.GetParameter(9)]}
    #pickle.dump( param, open( SIGNALFILE, "wb" ) )
    #print "Pickle signal file for channel", channel, "written to file", SIGNALFILE


    # Print
    #print "@  '"+channel+"' : {'mean' : [%e, %e], 'sigma' : [%e, %e], 'alpha' : [%e, %e], 'slope' : [%e, %e], 'norm' : [%e, %e, %e, %e, %e, %e, %e, %e, %e, %e]}," % ( fmean.GetParameter(0), fmean.GetParameter(1), fsigma.GetParameter(0), fsigma.GetParameter(1), falpha1.GetParameter(0), falpha1.GetParameter(1), fslope1.GetParameter(0), fslope1.GetParameter(1), fnorm.GetParameter(0), fnorm.GetParameter(1), fnorm.GetParameter(2), fnorm.GetParameter(3), fnorm.GetParameter(4), fnorm.GetParameter(5), fnorm.GetParameter(6), fnorm.GetParameter(7), fnorm.GetParameter(8), fnorm.GetParameter(9) )
    ##if HVTMODEL: print "@  param['"+channel+"']['norm_hvt'] : [%e, %e, %e]" % (fnorm.GetParameter(0), fnorm.GetParameter(1), fnorm.GetParameter(2))
    #else: print "@  "+channel+"   , 'norm_hvt' : [%e, %e, %e]" % (fnorm.GetParameter(0), fnorm.GetParameter(1), fnorm.GetParameter(2))
    #if isAH:
    #print "@  '"+channel+"' : {'mean' : [%e, %e], 'sigma' : [%e, %e], 'alpha1' : [%e, %e], 'slope1' : [%e, %e], 'alpha2' : [%e, %e], 'slope2' : [%e, %e], 'norm' : [%e, %e, %e, %e, %e, %e, %e, %e, %e, %e]}," % ( fmean.GetParameter(0), fmean.GetParameter(1), fsigma.GetParameter(0), fsigma.GetParameter(1), falpha1.GetParameter(0), falpha1.GetParameter(1), fslope1.GetParameter(0), fslope1.GetParameter(1), falpha2.GetParameter(0), falpha2.GetParameter(1), fslope2.GetParameter(0), fslope2.GetParameter(1), fnorm.GetParameter(0), fnorm.GetParameter(1), fnorm.GetParameter(2), fnorm.GetParameter(3), fnorm.GetParameter(4), fnorm.GetParameter(5), fnorm.GetParameter(6), fnorm.GetParameter(7), fnorm.GetParameter(8), fnorm.GetParameter(9) )
    # Save
#    outFile = TFile("rootfiles/fitDataHist.root", "UPDATE")
#    outFile.cd()
#    gmean.Write(channel+"_SignalMeanGraph")
#    fmean.Write(channel+"_SignalMeanFunction")
#    gsigma.Write(channel+"_SignalSigmaGraph")
#    fsigma.Write(channel+"_SignalSigmaFunction")
#    galpha.Write(channel+"_SignalAlphaGraph")
#    falpha.Write(channel+"_SignalAlphaFunction")
#    gslope.Write(channel+"_SignalSlopeGraph")
#    fslope.Write(channel+"_SignalSlopeFunction")
#    outFile.Close()
#    print "Histograms saved in file rootfiles/fitDataHist.root"



    if not gROOT.IsBatch(): raw_input("Press Enter to continue...")




        # Linear interpolation for the yield
#        idx = min(range(len(genPoints)), key=lambda x: abs(genPoints[x]-m) if genPoints[x]<=m and m!=genPoints[-1] else 1.e6)
#        m0, m1 = genPoints[idx], genPoints[idx+1]
#        y0, y1 = signalNorm[m0].getVal(), signalNorm[m1].getVal()
#        # y = y0 + (y1-y0)*(x-x0)/(x1-x0)
#        syield = y0 + (y1-y0)*(m-m0)/(m1-m0)




def efficiency(stype, Zlep=True):
    genPoints = [800, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000, 3500, 4000, 4500]
    eff = {}
    
    channels = [x for x in channelList if len(x)<5]

    for channel in channels:
        isAH = ('hp' in channel or 'lp' in channel)
        treeSign = {}
        ngenSign = {}
        nevtSign = {}
        eff[channel] = TGraphErrors()

        for i, m in enumerate(genPoints):
            if isAH and m < 1000: continue
            #if m==1600 or m==2000: continue
            signName = "%s_M%d" % (stype, m) #"%s_M%d" % (channel[:3], m)
            ngenSign[m] = 0.
            nevtSign[m] = 0.
            for j, ss in enumerate(sample[signName]['files']):
                if isAH and not 'had' in ss: continue
                if 'nn' in channel and not 'Zinv' in ss: continue
                if ('en' in channel or 'mn' in channel) and not 'Wlep' in ss: continue
                if ('ee' in channel or 'mm' in channel) and not 'Zlep' in ss: continue
                if Zlep and 'Zinv' in ss: continue
                if not Zlep and 'Zlep' in ss: continue

                sfile = TFile(NTUPLEDIR + ss + ".root", "READ")
                if not sfile.Get("Events")==None:
                    ngenSign[m] += sfile.Get("Events").GetEntries()
                    # From trees
                    treeSign[m] = sfile.Get("tree")
                    nevtSign[m] += treeSign[m].GetEntries(selection[channel] + selection['SR'])
                    # From hist
                    #nevtSign[m] += sfile.Get(channel+"SR/X_mass").GetEntries()
                else:
                    ngenSign[m] = -1
                    print "Failed reading file", NTUPLEDIR + ss + ".root"
                sfile.Close()
                #print channel, ss, ":", nevtSign[m], "/", ngenSign[m], "=", nevtSign[m]/ngenSign[m]
            if nevtSign[m] == 0 or ngenSign[m] < 0: continue
            # Gen Br
            #if ('en' in channel or 'mn' in channel or 'ee' in channel or 'mm' in channel): ngenSign[m] /= 1.5
            n = eff[channel].GetN()
            eff[channel].SetPoint(n, m, nevtSign[m]/ngenSign[m])
            eff[channel].SetPointError(n, 0, math.sqrt(nevtSign[m])/ngenSign[m])

        eff[channel].SetMarkerColor(color[channel])
        eff[channel].SetMarkerStyle(20)
        eff[channel].SetLineColor(color[channel])
        eff[channel].SetLineWidth(2)
        if channel.count('b')==1: eff[channel].SetLineStyle(3)

    n = max([eff[x].GetN() for x in channels])
    maxEff = 0.

    # Total efficiency
    eff["sum"] = TGraphErrors(n)
    eff["sum"].SetMarkerStyle(24)
    eff["sum"].SetMarkerColor(1)
    eff["sum"].SetLineWidth(2)
    for i in range(n):
        tot, mass = 0., 0.
        for channel in channels:
            if eff[channel].GetN() > i:
                tot += eff[channel].GetY()[i]
                mass = eff[channel].GetX()[i]
                if tot > maxEff: maxEff = tot
        eff["sum"].SetPoint(i, mass, tot)


    leg = TLegend(0.15, 0.60, 0.95, 0.8)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.SetNColumns(len(channels)/4)
    for i, channel in enumerate(channels):
        if eff[channel].GetN() > 0: leg.AddEntry(eff[channel], getChannel(channel), "pl")
    leg.SetY1(leg.GetY2()-len([x for x in channels if eff[x].GetN() > 0])/2.*0.045)

    legS = TLegend(0.55, 0.85-0.045, 0.95, 0.85)
    legS.SetBorderSize(0)
    legS.SetFillStyle(0) #1001
    legS.SetFillColor(0)
    legS.AddEntry(eff['sum'], "Total efficiency", "pl")

    c1 = TCanvas("c1", "Signal Efficiency", 1200, 800)
    c1.cd(1)
    eff['sum'].Draw("APL")
    for i, channel in enumerate(channels): eff[channel].Draw("SAME, PL")
    leg.Draw()
    legS.Draw()
    setHistStyle(eff["sum"], 1.1)
    eff["sum"].SetTitle(";m_{"+stype[1]+"'} (GeV);Acceptance #times efficiency")
    eff["sum"].SetMinimum(0.)
    eff["sum"].SetMaximum(max(1., maxEff*1.5)) #0.65
    eff["sum"].GetXaxis().SetTitleSize(0.045)
    eff["sum"].GetYaxis().SetTitleSize(0.045)
    eff["sum"].GetYaxis().SetTitleOffset(1.1)
    eff["sum"].GetXaxis().SetTitleOffset(1.05)
    eff["sum"].GetXaxis().SetRangeUser(750, 5000)
    if stype=='XWH' or (stype=='XZH' and Zlep): line = drawLine(750, 2./3., 4500, 2./3.)
    drawCMS(-1, "Simulation") #Preliminary
    drawAnalysis("VH")

    suffix = ""
    if isAH: suffix = "ah"
    elif stype=='XZH' and Zlep: suffix = "ll"
    elif stype=='XZH' and not Zlep: suffix = "nn"
    elif stype=='XWH': suffix = "ln"

    c1.Print("plotsSignal/Efficiency/"+stype+suffix+".pdf")
    c1.Print("plotsSignal/Efficiency/"+stype+suffix+".png")

    # print
    print "category",
    for m in range(0, eff["sum"].GetN()):
        print " & %d" % int(eff["sum"].GetX()[m]),
    print "\\\\", "\n\\hline"
    for i, channel in enumerate(channels+["sum"]):
        if channel=='sum': print "\\hline"
        print getChannel(channel).replace("high ", "H").replace("low ", "L").replace("purity", "P").replace("b-tag", ""),
        for m in range(0, eff[channel].GetN()):
            print "& %.1f" % (100.*eff[channel].GetY()[m]),
        print "\\\\"



def efficiencyAll():
    signals = {'XWHln' : ['enb', 'enbb', 'mnb', 'mnbb'], 'XZHll' : ['eeb', 'eebb', 'mmb', 'mmbb'], 'XZHnn' : ['nnb', 'nnbb'], 'AZhll' : ['eeb', 'eebb', 'mmb', 'mmbb'], 'AZhnn' : ['nnb', 'nnbb'], 'BBAZhll' : ['eeb', 'eebb', 'mmb', 'mmbb'], 'BBAZhnn' : ['nnb', 'nnbb'], 'monoH' : ['nnb', 'nnbb']}
    labels = {'XWHln' : "q#bar{q} #rightarrow W' #rightarrow Wh #rightarrow l#nub#bar{b}", 'XZHll' : "q#bar{q} #rightarrow Z' #rightarrow Zh #rightarrow llb#bar{b}", 'XZHnn' : "q#bar{q} #rightarrow Z' #rightarrow Zh #rightarrow #nu#nub#bar{b}", 'AZhll' : "gg #rightarrow A #rightarrow Zh #rightarrow llb#bar{b}", 'AZhnn' : "gg #rightarrow A #rightarrow Zh #rightarrow #nu#nub#bar{b}", 'BBAZhll' : "b#bar{b}A #rightarrow Zh #rightarrow llb#bar{b}", 'BBAZhnn' : "b#bar{b}A #rightarrow Zh #rightarrow #nu#nub#bar{b}", 'monoH' : "q#bar{q} #rightarrow Z' #rightarrow Ah #rightarrow #chi#chib#bar{b}"} # (m_{A}=300 GeV)
    #colors = {'XWHln' : 882, 'XZHll' : 418, 'XZHnn' : 856, 'AZhll' : 633, 'AZhnn' : 625, 'BBAZhll' : 633, 'BBAZhnn' : 625, 'monoH' : 602}
    colors = {'XWHln' : 1007, 'XZHll' : 1004, 'XZHnn' : 1003, 'AZhll' : 1006, 'AZhnn' : 1005, 'BBAZhll' : 1002, 'BBAZhnn' : 1003, 'monoH' : 1}
    styles = {'XWHln' : 1, 'XZHll' : 1, 'XZHnn' : 1, 'AZhll' : 2, 'AZhnn' : 2, 'BBAZhll' : 3, 'BBAZhnn' : 3, 'monoH' : 8}
    marker = {'XWHln' : 22, 'XZHll' : 21, 'XZHnn' : 20, 'AZhll' : 21, 'AZhnn' : 20, 'BBAZhll' : 25, 'BBAZhnn' : 24, 'monoH' : 24}
#    {'nnb' : 634, 'nnbb' : 634, 'enb' : 410, 'enbb' : 410, 'mnb' : 856, 'mnbb' : 856, 'eeb' : 418, 'eebb' : 418, 'mmb' : 602, 'mmbb' : 602, 'wrhpb': 634, 'wrhpbb': 634, 'wrlpb': 826, 'wrlpbb': 826, 'zrhpb': 856, 'zrhpbb': 856, 'zrlpb': 602, 'zrlpbb': 602, 'vrbbb' : 800, 'vrbbbb' : 801}
    genPoints = [800, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000, 3500, 4000, 4500]
    eff = {}
    
    for sign, channels in signals.iteritems():
        treeSign = {}
        ngenSign = {}
        nevtSign = {}
        eff[sign] = TGraphErrors()
        eff[sign].SetTitle(sign)
        eff[sign].SetMarkerColor(colors[sign])
        eff[sign].SetMarkerSize(1.25)
        eff[sign].SetLineColor(colors[sign])
        eff[sign].SetLineWidth(2)
        eff[sign].SetLineStyle(styles[sign])
        eff[sign].SetMarkerStyle(marker[sign])
        #if channel.count('b')==1: eff[channel].SetLineStyle(3)
        for i, m in enumerate(genPoints):
            neff = 0.
            for channel in channels:
                signName = "%s_M%d" % (sign, m)
                if 'AZh' in sign and m > 2000: continue
                if sign=='monoH' and m==1600: m = 1700
                if sign=='monoH' and m==1800: continue
                if sign=='monoH' and m>4000: continue
                if sign=='monoH': signName = "monoH_MZ%d_MA300" % (m)
                
                ngenSign[m] = 0.
                nevtSign[m] = 0.
                for j, ss in enumerate(sample[signName]['files']):
#                    if ('nn' in channel) and not ('inv' in channel): continue
#                    if ('en' in channel or 'mn' in channel) and not 'Wlep' in ss: continue
#                    if ('ee' in channel or 'mm' in channel) and not ('Zlep' in ss or 'LL' in ss): continue
                    #if Zlep and 'Zinv' in ss: continue
                    #if not Zlep and 'Zlep' in ss: continue
                    sfile = TFile(NTUPLEDIR + ss + ".root", "READ")
                    if not sfile.Get("Events")==None:
                        ngenSign[m] += sfile.Get("Events").GetEntries()
                        # From trees
                        treeSign[m] = sfile.Get("tree")
                        nevtSign[m] += treeSign[m].GetEntries(selection[channel] + selection['SR'])
                        # From hist
                        #nevtSign[m] += sfile.Get(channel+"SR/X_mass").GetEntries()
                    else:
                        ngenSign[m] = -1
                        print "Failed reading file", NTUPLEDIR + ss + ".root"
                    sfile.Close()
                    #print channel, ss, ":", nevtSign[m], "/", ngenSign[m], "=", nevtSign[m]/ngenSign[m]
                if nevtSign[m] == 0 or ngenSign[m] < 0: continue
                # Gen Br
                #if ('en' in channel or 'mn' in channel or 'ee' in channel or 'mm' in channel): ngenSign[m] /= 1.5
                neff += nevtSign[m]/ngenSign[m]
            if neff<=0.: continue
            if 'ln' in sign or 'll' in sign: neff *= 1.5
            n = eff[sign].GetN()
            eff[sign].SetPoint(n, m, neff)
            eff[sign].SetPointError(n, 0, 0)


    n = 0. #max([eff[x].GetN() for x in channels])
    maxEff = 0.

    leg = TLegend(0.15, 0.35, 0.95, 0.35)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    for sign in ['XZHnn', 'AZhll', 'XWHln', 'AZhnn', 'XZHll', 'BBAZhll', 'monoH', 'BBAZhnn']:
        if eff[sign].GetN() > 0:
            leg.AddEntry(eff[sign], labels[sign], "pl")
            n += 1
    leg.SetNColumns(int(n/3))
    leg.SetY1(leg.GetY2()-n*0.045/leg.GetNColumns())

#    legS = TLegend(0.55, 0.85-0.045, 0.95, 0.85)
#    legS.SetBorderSize(0)
#    legS.SetFillStyle(0) #1001
#    legS.SetFillColor(0)
#    legS.AddEntry(eff['sum'], "Total efficiency", "pl")

    c1 = TCanvas("c1", "Signal Efficiency", 1200, 800)
    c1.cd(1)
    c1.GetPad(0).SetTicks(1, 1)
    first = 'XZHnn'
    eff[first].Draw("APL")
    for sign, channels in signals.iteritems():
        eff[sign].Draw("APL" if i==0 else "SAME, PL")
    leg.Draw()
#    legS.Draw()
    setHistStyle(eff[first], 1.1)
    eff[first].SetTitle(";m_{X} (GeV);Acceptance #times efficiency")
    eff[first].SetMinimum(0.)
    eff[first].SetMaximum(max(1., maxEff*1.5)) #0.65
    eff[first].GetXaxis().SetTitleSize(0.045)
    eff[first].GetYaxis().SetTitleSize(0.045)
    eff[first].GetXaxis().SetLabelSize(0.045)
    eff[first].GetYaxis().SetLabelSize(0.045)
    eff[first].GetYaxis().SetTitleOffset(1.1)
    eff[first].GetXaxis().SetTitleOffset(1.05)
    eff[first].GetXaxis().SetRangeUser(750, 4500)
    eff[first].GetYaxis().SetRangeUser(0., 0.5)
#    if stype=='XWH' or (stype=='XZH' and Zlep): line = drawLine(750, 2./3., 4500, 2./3.)
    #drawCMS(-1, "Simulation", True)
    #drawAnalysis("XVHsl")

    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.05)
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextAlign(13)
    latex.DrawLatex(0.83, 0.99, "(13 TeV)")
    latex.SetTextFont(62)
    latex.SetTextSize(0.06)
    latex.DrawLatex(0.15, 0.90, "CMS")
    latex.SetTextSize(0.05)
    latex.SetTextFont(52)
#    latex.DrawLatex(0.15, 0.84, "Simulation")
    
#    suffix = ""
#    if isAH: suffix = "ah"
#    elif stype=='XZH' and Zlep: suffix = "ll"
#    elif stype=='XZH' and not Zlep: suffix = "nn"
#    elif stype=='XWH': suffix = "ln"

    c1.Print("plotsSignal/Efficiency/Efficiency.pdf")
    c1.Print("plotsSignal/Efficiency/Efficiency.png")



def plot(channel):
    # ====== CONTROL PLOT ======
    c_signal = TCanvas("c_signal", "c_signal", 800, 600)
    c_signal.cd()
    frame_signal = X_mass.frame()
    for m in genPoints[1:-1]: msignal[m].plotOn(frame_signal, RooFit.LineColor(sample["%s_M%d" % (channel[:3], m)]['linecolor']), RooFit.Normalization(1., RooAbsReal.NumEvent), RooFit.Name("M%d" % m))
    frame_signal.GetXaxis().SetRangeUser(XBINMIN, XBINMAX)
    frame_signal.GetYaxis().SetRangeUser(0, 1)
    frame_signal.GetYaxis().SetTitle("Arbitray units")
    frame_signal.Draw()
    drawCMS(-1, "Simulation")
    drawAnalysis("VH")
    drawRegion(channel)
    mleg = TLegend(0.75, 0.6, 0.98, 0.92)
    mleg.SetBorderSize(0)
    mleg.SetFillStyle(0) #1001
    mleg.SetFillColor(0)
    for m in genPoints[1:-1]: mleg.AddEntry("M%d" % m, "m_{X} = %d GeV" % m, "L")
    mleg.Draw()
    c_signal.SaveAs(PLOTDIR+"/"+channel+"/Signal.pdf")
    c_signal.SaveAs(PLOTDIR+"/"+channel+"/Signal.png")
    if VERBOSE: raw_input("Press Enter to continue...")
    # ====== CONTROL PLOT ======

#efficiency()
#exit()
#signal("XZHnnb")
#signal("XZHhpb")

#for c in channelList: #signal(c)
#    p = multiprocessing.Process(target=signal, args=(c,))
#    jobs.append(p)
#    p.start()


if __name__ == "__main__":
    if options.efficiency:
#        for s in ['XWH', 'XZH']: #signalList:
#            efficiency(s)
#        efficiency('XZH', False)
        efficiencyAll()

    elif options.all:
        gROOT.SetBatch(True)
        for s in signalList:
            for c in channelList:
                if PARALLELIZE:
                    p = multiprocessing.Process(target=signal, args=(c, s,))
                    jobs.append(p)
                    p.start()
                else:
                    signal(c, s)
    else:
        signal(options.channel, options.signal)


# python parametrization.py | grep @ > parameters_.py
