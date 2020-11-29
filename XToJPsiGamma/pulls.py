#! /usr/bin/env python

import os, multiprocessing
import copy
import math
from array import array
from ROOT import ROOT, gROOT, gStyle, gRandom, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TH1F, TH2F, THStack, TGraph, TGraphAsymmErrors
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TLine, TPaveText

from plotUtils import *

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-b", "--bash", action="store_true", default=False, dest="bash")
parser.add_option("-f", "--fileName", action="store", type="string", dest="fileName", default="pulls.txt")
parser.add_option("-o", "--outName", action="store", type="string", dest="outName", default="pulls")
(options, args) = parser.parse_args()
if options.bash: gROOT.SetBatch(True)

fileName = options.fileName
outName = options.outName

# Format:
#0 : sys name
#1 : b-only DX
#2 : b-only dDX
#3 : s+b DX
#4 : s+b dDX
#5 : rho

gStyle.SetOptStat(0)
gStyle.SetErrorX(0)


def pulls(fileName):
    with open(fileName) as f:
        content = f.readlines()

    content_nostat = [x for x in content if not 'CMS_stat' in x]

    nbins, off = len(content_nostat), 0.10
    b_pulls = TH1F("b_pulls", ";;Pulls", nbins, 0.-off, nbins-off)
    s_pulls = TH1F("s_pulls", ";;Pulls", nbins, 0.+off, nbins+off) #

    for i, s in enumerate(content_nostat):
        l = s.split()
        b_pulls.GetXaxis().SetBinLabel(i+1, l[0])
        s_pulls.GetXaxis().SetBinLabel(i+1, l[0])
        b_pulls.SetBinContent(i+1, float(l[1]))
        b_pulls.SetBinError(i+1, float(l[2]))
        s_pulls.SetBinContent(i+1, float(l[3]))
        s_pulls.SetBinError(i+1, float(l[4]))

    b_pulls.SetFillStyle(3005)
    b_pulls.SetFillColor(923)
    b_pulls.SetLineColor(923)
    b_pulls.SetLineWidth(2)
    b_pulls.SetMarkerStyle(20)
    b_pulls.SetMarkerSize(1.25)

    s_pulls.SetLineColor(602)
    s_pulls.SetMarkerColor(602)
    s_pulls.SetMarkerStyle(24) #24
    s_pulls.SetLineWidth(2)

    b_pulls.GetYaxis().SetRangeUser(-2.5, 2.5)


    c1 = TCanvas("c1", "Pulls", 1600, 800)
    c1.cd()
    c1.GetPad(0).SetTopMargin(0.06)
    c1.GetPad(0).SetRightMargin(0.05)
    c1.GetPad(0).SetBottomMargin(0.15)
    c1.GetPad(0).SetTicks(1, 1)

    #    box = TBox(950., 105., 2000., 200.)
    #    box.SetFillStyle(3354)
    #    #box.SetFillStyle(0)
    #    box.SetFillColor(1)
    #    box.SetLineWidth(2)
    #    box.SetLineStyle(2)
    #    box.SetLineColor(1)
    #    box.Draw()

    # Draw
    b_pulls.Draw("PE1")
    #b_pulls.Draw("B")
    s_pulls.Draw("SAME, PE1")

    leg = TLegend(0.25, 0.95, 0.75, 0.995)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetFillColor(0)
    leg.SetNColumns(2)
    leg.AddEntry(b_pulls,  "background-only fit", "flp")
    leg.AddEntry(s_pulls,  "signal+background fit", "lp")

    line = TLine()
    line.DrawLine(0., 0., nbins, 0.)
    line.SetLineStyle(7)
    line.SetLineWidth(2)
    line.SetLineColor(417)
    line.DrawLine(0., 1., nbins, 1.)
    line.DrawLine(0., -1., nbins, -1.)
    line.SetLineColor(800)
    line.DrawLine(0., 2., nbins, 2.)
    line.DrawLine(0., -2., nbins, -2.)


    leg.Draw()
    #    drawCMS(LUMI, "Simulation")
    #    drawAnalysis("DM")
    #    drawRegion(channel)

    #    c1.Print(outName+".jpg")
    c1.Print(outName+".png")
    c1.Print(outName+".pdf")

    if not gROOT.IsBatch(): raw_input("Press Enter to continue...")



def pullsVertical(fileName):

    with open(fileName) as f:
        content = f.readlines()

    content_nostat = [x for x in content if not 'CMS_stat' in x]

    nbins, off = len(content_nostat), 0.10
    
    b_pulls = TH1F("b_pulls", ";;Pulls", nbins, 0.-off, nbins-off)
    s_pulls = TH1F("s_pulls", ";;Pulls", nbins, 0.+off, nbins+off) #

    for i, s in enumerate(content_nostat):
        l = s.split()
        if len(l)==0 or "name" in l[0]: continue
        b_pulls.GetXaxis().SetBinLabel(i+1, l[0])
        s_pulls.GetXaxis().SetBinLabel(i+1, l[0])
        b_pulls.SetBinContent(i+1, float(l[1]))
        b_pulls.SetBinError(i+1, float(l[2]))
        s_pulls.SetBinContent(i+1, float(l[3]))
        s_pulls.SetBinError(i+1, float(l[4]))

    b_pulls.SetFillStyle(3005)
    b_pulls.SetFillColor(923)
    b_pulls.SetLineColor(923)
    b_pulls.SetLineWidth(1)
    b_pulls.SetMarkerStyle(20)
    b_pulls.SetMarkerSize(1.25)

    s_pulls.SetLineColor(602)
    s_pulls.SetMarkerColor(602)
    s_pulls.SetMarkerStyle(24) #24
    s_pulls.SetLineWidth(1)

    b_pulls.GetYaxis().SetRangeUser(-2.5, 2.5)


    # Graphs
    h_pulls = TH2F("pulls", "", 6, -3., 3., nbins, 0, nbins)
    B_pulls = TGraphAsymmErrors(nbins)
    S_pulls = TGraphAsymmErrors(nbins)

    boxes = []

    c1 = TCanvas("c1", "Pulls", 600, 150+nbins*10)#nbins*20)
    c1.cd()
    c1.SetGrid(0, 1)
    c1.GetPad(0).SetTopMargin(0.01)
    c1.GetPad(0).SetRightMargin(0.01)
    c1.GetPad(0).SetBottomMargin(0.10)
    c1.GetPad(0).SetLeftMargin(0.25)#(0.25)#(0.065)
    c1.GetPad(0).SetTicks(1, 1)

    for i, s in enumerate(content_nostat):
        l = s.split()
        if len(l)==0 or "name" in l[0]: continue
        if "1034h" in l[0]: l[0]="CMS_PDF_13TeV"
        h_pulls.GetYaxis().SetBinLabel(i+1, l[0].replace('CMS2016_', ''))#C
#        y1 = gStyle.GetPadBottomMargin()
#        y2 = 1. - gStyle.GetPadTopMargin()
#        h = (y2 - y1) / float(nbins)
#        y1 = y1 + float(i) * h
#        y2 = y1 + h
#        box = TPaveText(0, y1, 1, y2, 'NDC')
#        box.SetFillColor(0)
#        box.SetTextSize(0.02)
#        box.SetBorderSize(0)
#        box.SetTextAlign(12)
#        box.SetMargin(0.005)
#        if i % 2 == 0:
#            box.SetFillColor(18)
#        box.Draw()
#        boxes.append(box)
        B_pulls.SetPoint(i+1,float(l[1]),float(i+1)-0.3)#C
        B_pulls.SetPointError(i+1,float(l[2]),float(l[2]),0.,0.)#C

    for i, s in enumerate(content_nostat):
        l = s.split()
        if len(l)==0 or "name" in l[0]: continue
        S_pulls.SetPoint(i+1,float(l[3]),float(i+1)-0.7)#C
        S_pulls.SetPointError(i+1,float(l[4]),float(l[4]),0.,0.)#C

    h_pulls.GetXaxis().SetTitle("(#hat{#theta} - #theta_{0}) / #Delta#theta")
    h_pulls.GetXaxis().SetLabelOffset(0.01)
    h_pulls.GetXaxis().SetTitleOffset(1.)
    h_pulls.GetYaxis().SetNdivisions(nbins, 0, 0)
    
    B_pulls.SetFillColor(1)
    B_pulls.SetLineColor(1)
    B_pulls.SetLineStyle(1)
    B_pulls.SetLineWidth(2)
    B_pulls.SetMarkerColor(1)
    B_pulls.SetMarkerStyle(20)
    B_pulls.SetMarkerSize(1)#(0.75)

    S_pulls.SetFillColor(629)
    S_pulls.SetLineColor(629)
    S_pulls.SetMarkerColor(629)
    S_pulls.SetLineWidth(2)
    S_pulls.SetMarkerStyle(20)
    S_pulls.SetMarkerSize(1)
    
    box1 = TBox(-1., 0., 1., nbins)
    box1.SetFillStyle(3001)
    #box1.SetFillStyle(0)
    box1.SetFillColor(417)
    box1.SetLineWidth(2)
    box1.SetLineStyle(2)
    box1.SetLineColor(417)
    
    box2 = TBox(-2., 0., 2., nbins)
    box2.SetFillStyle(3001)
    #box2.SetFillStyle(0)
    box2.SetFillColor(800)
    box2.SetLineWidth(2)
    box2.SetLineStyle(2)
    box2.SetLineColor(800)
    
    leg = TLegend(0.1, 0., 0.7, 0.05)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetFillColor(0)
    leg.SetNColumns(2)
    leg.AddEntry(B_pulls,  "B-only fit", "lp")
    leg.AddEntry(S_pulls,  "S+B fit", "lp")
    
    h_pulls.Draw("")
    box2.Draw()
    box1.Draw()
    B_pulls.Draw("P6SAME")
    S_pulls.Draw("P6SAME")
    leg.Draw()
    
#    drawCMS(35867, "Preliminary")
#    drawAnalysis("VH")
#    drawRegion(outName)
    
    c1.Print(outName+".png")
    c1.Print(outName+".pdf")

    if not gROOT.IsBatch(): raw_input("Press Enter to continue...")




pullsVertical(fileName)
