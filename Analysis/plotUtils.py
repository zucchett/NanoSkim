import os, multiprocessing
import copy
import math
from array import array
from ROOT import ROOT, gROOT, gStyle, gRandom, gDirectory, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TH1, TH1D, TH1F, TH2F, THStack, TGraph, TGraphAsymmErrors
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TLine, TBox, TMath

#from samples import sample
#from variables import variable
#NTUPLEDIR   = "/lustre/cmsdata/zucchett/SameSign/Gruppo2/"
NTUPLEDIR   = "/lustre/cmsdata/zucchett/Higgs/v0/"

##################
# ANALYSIS UTILS #
##################


def project(s, pd, var, cut):

    hist = TH1F(s, ";"+var['title']+";Events;"+('logx' if var['logx'] else '')+('logy' if var['logy'] else ''), var['nbins'], var['min'], var['max'])
    if var['nbins'] <= 0: hist = TH1F(s, ";"+var['title']+";Events;"+";Events;"+('logx' if var['logx'] else '')+('logy' if var['logy'] else ''), len(var['bins'])-1, array('f', var['bins']))
    hist.Sumw2()
    
    nfiles = 0
    tree = TChain("Events")
    for j, ss in enumerate(sample[s]['files']):
        if not 'data' in s or ('data' in s and ss in pd):
            for f in os.listdir(NTUPLEDIR + '/' + ss):
                if f.endswith(".root"):
                    tree.Add(NTUPLEDIR + '/' + ss + '/' + f)
                    nfiles += 1
    print "Projecting", s, "from", nfiles, "files"
    tree.Project(s, var['var'], cut)
    hist.SetDirectory(0)
#    tree.Draw("%s>>%s" % (var, s), cut, "goff")
#    hist = gDirectory.Get(s)
    if not tree.GetTree()==None: hist.SetOption("%s" % tree.GetTree().GetEntriesFast())
    return hist


def projectLoop(s, pd, var, cut, verbose=True):

    hist = TH1F(s, ";"+var['title']+";Events;"+('logx' if var['logx'] else '')+('logy' if var['logy'] else ''), var['nbins'], var['min'], var['max'])
    if var['nbins'] <= 0: hist = TH1F(s, ";"+var['title']+";Events;"+('logx' if var['logx'] else '')+('logy' if var['logy'] else ''), len(var['bins'])-1, array('f', var['bins']))
    hist.Sumw2()
    hist.SetDirectory(0)
    
    for j, ss in enumerate(sample[s]['files']):
        nfiles = 0
        if not 'data' in s or ('data' in s and ss in pd):
            for f in os.listdir(NTUPLEDIR + '/' + ss):
                if not f.endswith(".root"): continue
                tmpFile = TFile(NTUPLEDIR + '/' + ss + '/' + f, "READ")
                tmpHist = hist.Clone(s + "_" + f)
                tmpHist.Reset()
                tree = tmpFile.Get("Events")
                tree.Project(s + "_" + f, var['var'], cut)
                hist.Add(tmpHist)
                tmpFile.Close()
                if verbose: print ' + ', ss[:25], '\t', nfiles, '\r',
                nfiles += 1
        if verbose: print ''
        else: print '+ ', ss[:20], '\t', nfiles
    return hist


def loopProject(s, ss, var, cut, verbose=True):

    hist = TH1F(ss, ";"+var['title']+";Events;"+('logx' if var['logx'] else '')+('logy' if var['logy'] else ''), var['nbins'], var['min'], var['max'])
    if var['nbins'] <= 0: hist = TH1F(ss, ";"+var['title']+";Events;"+('logx' if var['logx'] else '')+('logy' if var['logy'] else ''), len(var['bins'])-1, array('f', var['bins']))
    hist.Sumw2()
    hist.SetOption(s)
    hist.SetDirectory(0)
    
    nfiles = 0
    for f in os.listdir(NTUPLEDIR + '/' + ss):
        if not f.endswith(".root"): continue
        
        tmpFile = TFile(NTUPLEDIR + '/' + ss + '/' + f, "READ")
        tree = tmpFile.Get("Events")
        tmpHist = hist.Clone(ss + "_" + f)
        tmpHist.Reset()
        print tmpFile.ls()
        tree.Project(ss + "_" + f, var['var'], cut)
        #tree.Draw(var['var'] + ">>" + ss + "_" + f, cut, "goff")
        hist.Add(tmpHist)
        tmpFile.Close()
        nfiles += 1
    if verbose: print '+ ', ss[:25], ' '*10, nfiles
    return hist
    


def parallelProject(queue, s, ss, var, cut, verbose=True):

    hist = TH1F(ss, ";"+var['title']+";Events;"+('logx' if var['logx'] else '')+('logy' if var['logy'] else ''), var['nbins'], var['min'], var['max'])
    if var['nbins'] <= 0: hist = TH1F(ss, ";"+var['title']+";Events;"+('logx' if var['logx'] else '')+('logy' if var['logy'] else ''), len(var['bins'])-1, array('f', var['bins']))
    hist.Sumw2()
    hist.SetOption(s)
    hist.SetDirectory(0)
    
    
#    if ss.startswith('ZGTo2LG_') or ss.startswith('ZGToLLG_'): cut += "*((Sum$(GenPart_pdgId==22 && GenPart_statusFlags==0 && GenPart_pt>15. && abs(GenPart_eta)<2.6)>0 && Sum$((abs(GenPart_pdgId)==11 || abs(GenPart_pdgId)==13 || abs(GenPart_pdgId)==15) && GenPart_statusFlags==0 && GenPart_pt>15.)>=2))"
#    if ss.startswith('DYJetsToLL_M-50_TuneC'): cut += "*(!(Sum$(GenPart_pdgId==22 && GenPart_statusFlags==0 && GenPart_pt>15. && abs(GenPart_eta)<2.6)>0 && Sum$((abs(GenPart_pdgId)==11 || abs(GenPart_pdgId)==13 || abs(GenPart_pdgId)==15) && GenPart_statusFlags==0 && GenPart_pt>15.)>=2))"
#    '( !(Sum$(PhotonGen_isPrompt==1 && PhotonGen_pt>15 && abs(PhotonGen_eta)<2.6) > 0 && Sum$(LeptonGen_isPrompt==1 && LeptonGen_pt>15)>=2) )'
#    
#    if ss.startswith('ZGTo2LG_') or ss.startswith('ZGToLLG_'): cut += "*(Sum$(LHEPart_pdgId==22 && abs(LHEPart_eta)<2.6 && LHEPart_pt>15.)>0)"
#    if ss.startswith('DYJetsToLL_M-50_TuneC'): cut += "*(Sum$(LHEPart_pdgId==22 && abs(LHEPart_eta)<2.6 && LHEPart_pt>15.)==0)"
    
#    if ss.startswith('ZGTo2LG_TuneCUETP8M1'): cut += "*(Sum$(GenPart_pdgId == 22 && TMath::Odd(GenPart_statusFlags) && GenPart_pt > 15.)>0)"
#    if ss.startswith('ZGToLLG_01J_5f_TuneCP5'): cut += "*(Sum$(GenPart_pdgId == 22 && TMath::Odd(GenPart_statusFlags) && GenPart_pt > 20.)>0)"
#    if ss.startswith('DYJetsToLL_M-50_TuneCUETP8M1'): cut += "*(Sum$(GenPart_pdgId == 22 && TMath::Odd(GenPart_statusFlags) && GenPart_pt > 15.)==0)"
#    if ss.startswith('DYJetsToLL_M-50_TuneCP5'): cut += "*(Sum$(GenPart_pdgId == 22 && TMath::Odd(GenPart_statusFlags) && GenPart_pt > 20.)==0)"
    
    nfiles = 0
    for f in os.listdir(NTUPLEDIR + '/' + ss):
        if not f.endswith(".root"): continue
        tmpFile = TFile(NTUPLEDIR + '/' + ss + '/' + f, "READ")
        tmpHist = hist.Clone(ss + "_" + f)
        tmpHist.Reset()
        tree = tmpFile.Get("Events")
        tree.Project(ss + "_" + f, var['var'], cut)
        hist.Add(tmpHist)
        tmpFile.Close()
        nfiles += 1
    if verbose: print '+ ', ss[:25], ' '*10, nfiles
    queue.put( hist )
    


def readhist(filename, s, var, cat):
    file = TFile(filename, "READ")
    if file.IsZombie():
        print "WARNING: file", filename, "does not exist"
        return None
    h = file.Get(cat + '/' + var + "/" + s)
    h.SetDirectory(0)     
    return h



def readaddhist(s, pd, var, directory):

    hist = None
    hist.SetDirectory(0)
    
    for j, ss in enumerate(sample[s]['files']):
        if not 'data' in s or ('data' in s and ss in pd):
            for f in os.listdir(NTUPLEDIR + '/' + ss):
                if f.endswith(".root"):
                    file = TFile(NTUPLEDIR + ss + f, "R")
                    if file.IsZombie():
                        print "WARNING: file", NTUPLEDIR + ss + ".root", "does not exist"
                        continue
                    tmphist = file.Get(directory + "/" + var)
                    if tmphist==None: continue
                    if s == None: hist = tmphist
                    else: hist.Add(tmphist)
    hist.Scale(sample[s]['weight'] if hist.Integral() >= 0 else 0)
    hist.SetFillColor(sample[s]['fillcolor'])
    hist.SetFillStyle(sample[s]['fillstyle'])
    hist.SetLineColor(sample[s]['linecolor'])
    hist.SetLineStyle(sample[s]['linestyle'])
    return hist




def printTable(hist, sign=[]):
    
    samples = [x for x in sorted(hist, key=lambda h : hist[h].Integral(), reverse=True) if not 'data' in x and not 'BkgSum' in x and not x in sign]
    print "Sample                  Events          Entries         %"
    print "-"*60
    for i, s in enumerate(['data_obs']+samples+['BkgSum']):
        if i==1 or i==len(samples)+1: print "-"*60
        print "%-20s" % s, "\t%-10.2f" % hist[s].Integral(), "\t%-10.0f" % (hist[s].GetEntries()), "\t%-10.2f" % (100.*hist[s].Integral()/hist['BkgSum'].Integral()) if hist['BkgSum'].Integral() > 0 else 0
    print "-"*60
    for i, s in enumerate(sign):
        #if not sample[s]['plot']: continue
        print "%-20s" % s, "\t%-10.2f" % hist[s].Integral(), "\t%-10.0f" % (hist[s].GetEntries()), "\t%-10.2f" % 0.
    print "-"*60




def addSystematics():
    # Read Histograms
    hist = []
    histFile = TFile("rootfiles/monoX.root", "READ")
    for k, s in enumerate(sample):
        hist.append(histFile.Get(s))
        print hist[k].GetName(), hist[k].Integral() 
    hist.append(histFile.Get("AllBkg"))
    
    # Read systematics
    ns = 10
    sysUp = []
    sysDown = []
    sysFile = TFile("rootfiles/systematics.root", "READ")
    for k in range(ns):
        up = sysFile.Get("Sys%dUp" % k)
        down = sysFile.Get("Sys%dDown" % k)
        sysUp.append(up)
        sysDown.append(down)
    #sysFile.Close()
    
    
    outFile = TFile("rootfiles/monoX.root", "RECREATE")
    outFile.cd()
    hist[0].SetName("data_obs")
    hist[0].Write("data_obs")
    for i, s in list(enumerate(sample[1:])):
        name = hist[i+1].GetName()
        hist[i+1].Write()
        outFile.mkdir("Sys"+name)
        outFile.cd("Sys"+name)
        for k in range(10):
            up = hist[i+1].Clone(name+"_Sys%dUp" % k)
            up.Multiply(sysUp[k])
            up.Write()
            down = hist[i+1].Clone(name+"_Sys%dDown" % k)
            down.Multiply(sysDown[k])
            down.Write()
        outFile.cd()
    hist[len(hist)-1].Write("AllBkg")
    outFile.Close()


def convertHistToGraph(hist, useGarwood=False):
    alpha = 1 - 0.6827
    graph = TGraphAsymmErrors(hist.GetNbinsX())
    if useGarwood:
        lastEvent = False
        for i in reversed(range(hist.GetNbinsX())):
            N = hist.GetBinContent(i+1)
            if not lastEvent and N > 0: lastEvent = True
            if lastEvent and N<=0.: N = 1.e-6
            L = 0 if N==0 else ROOT.Math.gamma_quantile(alpha/2, N, 1.)
            U = ROOT.Math.gamma_quantile_c(alpha/2, N+1, 1)
            graph.SetPoint(i, hist.GetXaxis().GetBinCenter(i+1), N if not N==0 else -1.e99)
            graph.SetPointError(i, 0., 0., N-L, U-N)
    else:
        for i in range(hist.GetNbinsX()):
            graph.SetPoint(i, hist.GetXaxis().GetBinCenter(i+1), hist.GetBinContent(i+1))
            graph.SetPointError(i, hist.GetXaxis().GetBinWidth(i+1)/2., hist.GetXaxis().GetBinWidth(i+1)/2., hist.GetBinError(i+1), hist.GetBinError(i+1))
        
    graph.SetLineWidth(hist.GetLineWidth())
    graph.SetLineStyle(hist.GetLineStyle())
    graph.SetLineColor(hist.GetLineColor())
    graph.SetMarkerSize(hist.GetMarkerSize())
    graph.SetMarkerStyle(hist.GetMarkerStyle())
    graph.SetMarkerColor(hist.GetMarkerColor())
    graph.SetFillStyle(hist.GetFillStyle())
    graph.SetFillColor(hist.GetFillColor())
    return graph

def makeResidHist(data, bkg):
    pulls = TGraphAsymmErrors(data.GetN())
    pulls.SetName("Pulls")
    pulls.SetLineWidth(data.GetLineWidth())
    pulls.SetLineStyle(data.GetLineStyle())
    pulls.SetLineColor(data.GetLineColor())
    pulls.SetMarkerSize(data.GetMarkerSize())
    pulls.SetMarkerStyle(data.GetMarkerStyle())
    pulls.SetMarkerColor(data.GetMarkerColor())
    pulls.SetFillStyle(data.GetFillStyle())
    pulls.SetFillColor(data.GetFillColor())
    
    # Add histograms, calculate Poisson confidence interval on sum value
    for i in range(data.GetN()):
        x = data.GetX()[i]
        dyl = data.GetErrorYlow(i)
        dyh = data.GetErrorYhigh(i)
        yy = data.GetY()[i] - bkg.Interpolate(x) #bkg.GetBinContent(i+1)
        norm = dyl if yy>0. else dyh
        if norm == 0.:
            yy, dyh, dyl = 0., 0., 0.
        else:
            yy /= norm
            dyh /= norm
            dyl /= norm
        pulls.SetPoint(i, x, yy)
        pulls.SetPointEYhigh(i, dyh)
        pulls.SetPointEYlow(i, dyl)

    return pulls

##################
### DRAW UTILS ###
##################

def getChannel(channel):
    text = ""
    #
    if 'Electrons' in channel: return "2e, 2 jets"
    elif 'Muons' in channel: return "2#mu, 2 jets"
    elif 'MET' in channel: return "0l, 2 jets"
    isAH = ('hp' in channel or 'lp' in channel or 'qqqq' in channel)
    #
    if 'ah' in channel: return "All categories"
    if 'VHsl' in channel: return "0l, 1l, 2l categories"
    if 'WHsl' in channel: return "1l categories"
    if 'ZHsl' in channel: return "0l, 2l categories"
    if 'sum' in channel: return "Total"
    # leptons
    if 'nn' in channel or '0l' in channel: text += "0l"
    elif 'ee' in channel or '2e' in channel: text += "2e"
    elif 'e' in channel or '1e' in channel: text += "1e"
    elif 'mm' in channel or '2m' in channel: text += "2#mu"
    elif 'm' in channel or '1m' in channel: text += "1#mu"
    elif 'll' in channel or '2l' in channel: text += "2l"
    elif 'ln' in channel or '2l' in channel: text += "1l"
    #if 'qq' in channel or 'hp' in channel or 'lp' in channel: text += "all-had"
    if 'sb' in channel: text += "sidebands"
    elif 'zr' in channel: text += "Z mass"
    elif 'wr' in channel: text += "W mass"
    elif 'vr' in channel: text += "V b tag"
    # purity
    if 'hp' in channel: text += ", high purity"
    elif 'lp' in channel: text += ", low purity"
    elif 'ap' in channel: text += ", no purity"
    # b-tag
    if '0b' in channel: text += ", no b tag" if isAH else ", 0 b tag"
    elif 'bbbb' in channel or '4b' in channel: text += ", tight b tag" if isAH else ", 4 b tag"
    elif 'bbb' in channel or '3b' in channel: text += ", loose b tag" if isAH else ", 3 b tag"
    elif 'bb' in channel or '2b' in channel: text += ", tight b tag" if isAH else ", 2 b tag"
    elif 'b' in channel or '1b' in channel: text += ", loose b tag" if isAH else ", 1 b tag"
    # region
    if 'SR' in channel: text += ", signal region"
    elif 'SB' in channel: text += ", sidebands region"
    elif 'CR' in channel: text += ", control region"
    elif 'TR' in channel: text += ", top control region"
    elif 'WR' in channel: text += ", W control region"
    elif 'ZR' in channel: text += ", Z control region"
    elif 'MC' in channel: text += ", simulation"
    elif 'Inc' in channel: text += ", inclusive region"
    
    return text

def drawCMS(lumi, text, onTop=False):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.045)
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextAlign(33)
    if (type(lumi) is float or type(lumi) is int):
        if float(lumi) > 0: latex.DrawLatex(0.95, 0.99, "%.1f fb^{-1}  (13 TeV)" % (float(lumi)/1000.))
        else: latex.DrawLatex(0.95, 0.99, "(13 TeV)")
    elif type(lumi) is str: latex.DrawLatex(0.95, 0.985, "%s  (13 TeV)" % lumi)
    if not onTop: latex.SetTextAlign(11)
    latex.SetTextFont(62)
    latex.SetTextSize(0.05 if len(text)>0 else 0.06)
    if not onTop: latex.DrawLatex(0.15, 0.88 if len(text)>0 else 0.85, "CMS")
    else: latex.DrawLatex(0.24, 0.9925, "CMS")
    latex.SetTextSize(0.04)
    latex.SetTextFont(52)
    if not onTop: latex.DrawLatex(0.15, 0.84, text)
    else: latex.DrawLatex(0.45, 0.98, text)
#    latex.SetTextSize(0.04)
#    latex.SetTextFont(62)
#    latex.SetTextAlign(13)
#    latex.DrawLatex(0.45, 0.98, "DM monojet")

def drawAnalysis(s, center=False):
    text = ""
    if s.startswith('X'):
        if 'ah' in s or 'qq' in s or 'hp' in s or 'lp' in s or 'ap' in s or 'sb' in s:
            if "ZH" in s: text = "X #rightarrow Zh #rightarrow q#bar{q}b#bar{b}"
            elif "WH" in s: text = "X #rightarrow Wh #rightarrow q#bar{q}b#bar{b}"
            else: text = "X #rightarrow Vh #rightarrow q#bar{q}b#bar{b}"
        elif 'mm' in s or 'ee' in s or 'mn' in s or 'en' in s or 'nn' in s: text = "X #rightarrow Vh #rightarrow (#nu#nu,l#nu,ll)b#bar{b}"
        elif "ZH" in s: text = "Z' #rightarrow Zh #rightarrow (#nu#nu,ll)bb"
        elif "WH" in s: text = "W' #rightarrow Wh #rightarrow l#nu bb"
        elif "sl" in s: text = "V' #rightarrow Vh #rightarrow (#nu#nu,l#nu,ll)bb"
    elif "AZh" in s: text = "A #rightarrow Zh #rightarrow (#nu#nu,ll)bb"
    elif "DM" in s or "CR" in s: text = "DM + heavy flavour"
    elif "monoH" in s: text = "Z' #rightarrow Ah #rightarrow #chi#chi b#bar{b}"
    else: return True
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.045)
    latex.SetTextFont(42)
    #latex.SetTextAlign(33)
    latex.DrawLatex(0.15 if not center else 0.25, 0.95, text)

def drawRegion(text, left=False):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextFont(72) #52
    latex.SetTextSize(0.04)
    if left: latex.DrawLatex(0.15, 0.79, text)
    else:
        latex.SetTextAlign(22)
        latex.DrawLatex(0.5, 0.85, text)

def drawOverflow():
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextAngle(90)
    latex.SetTextSize(0.03)
    #latex.SetTextColor(1)
    latex.SetTextFont(42)
    #latex.SetTextAlign(33)
    latex.DrawLatex(0.97, 0.02, "Overflow")

def drawBox(x1, y1, x2, y2, t=""):
    box = TBox(x1, y1, x2, y2)
    box.SetFillColor(1)
    box.SetFillStyle(3004)
    box.Draw()
    if not t=="":
        text = TLatex()
        text.SetTextColor(1)
        text.SetTextFont(42)
        text.SetTextAlign(23)
        text.SetTextSize(0.04)
        text.DrawLatex((x1+x2)/2., y2/1.15, t)
        text.Draw()
    return box

def drawLine(x1, y1, x2, y2):
    line = TLine(x1, y1, x2, y2)
    line.SetLineStyle(2)
    line.SetLineWidth(2)
    line.Draw()
    return line

def drawText(x, y, t, isNDC=False):
    text = TLatex()
    text.SetTextColor(1)
    text.SetTextFont(42)
    text.SetTextAlign(23)
    text.SetTextSize(0.04)
    if isNDC: text.DrawLatexNDC(x, y, t)
    else: text.DrawLatex(x, y, t)
    text.Draw()
    return text


def drawMass(m):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextAlign(22)
    latex.SetTextSize(0.04)
    if type(m)==int: latex.DrawLatex(0.75, 0.85, "m_{X} = %.0f GeV" % m)
    else: latex.DrawLatex(0.75, 0.85, m)
    
def draw2HDM(t, m=0):
    ttype = ""
    if t=='1': ttype = "Type-I"
    elif t=='2': ttype = "Type-II"
    elif t=='3': ttype = "Type-III"
    elif t=='4': ttype = "Type-IV"
    else:
        print "2HDM type not recognized"
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(72)
    latex.SetTextSize(0.04)
    latex.DrawLatex(0.15, 0.875, ttype + " 2HDM")
    latex.SetTextFont(42)
    if m > 0: latex.DrawLatex(0.15, 0.8, "m_{A}=%d GeV" % m)

def drawChi2(chi2, ndf=1, prob=False):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(62)
    latex.SetTextSize(0.08)
    if prob: latex.DrawLatex(0.65, 0.85, "#chi^{2}/ndf = %.1f/%.0f     p-value = %.2f" % (chi2, ndf, TMath.Prob(chi2, ndf)))
    elif ndf==1: latex.DrawLatex(0.75, 0.85, "#chi^{2} = %.3f" % chi2)
    else: latex.DrawLatex(0.75, 0.85, "#chi^{2}/ndf = %.1f/%.0f" % (chi2, ndf))

def drawKS(data, bkg):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(62)
    latex.SetTextSize(0.08)
    latex.DrawLatex(0.65, 0.85, "K-S p-value = %.3f" % (data.KolmogorovTest(bkg)))

def drawMediator(med):
    text = "Pseudoscalar" if 'ps' in med else "Scalar"
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextFont(42)
    latex.DrawLatex(0.15, 0.70, text+" mediator") #, g_{#Phi q#bar{q}} Yukawa
    latex.DrawLatex(0.15, 0.65, "g_{q}=1,   m_{#chi}=1 GeV")


def drawNorm(y, text, secondline=""):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.SetTextSize(0.032)
    latex.DrawLatex(0.71, y, text)
    if len(secondline) > 0: latex.DrawLatex(0.71, y-0.045, secondline)
    
def drawRatio(data, bkg):
    errData = array('d', [1.0])
    errBkg = array('d', [1.0])
    intData = data.IntegralAndError(1, data.GetNbinsX(), errData)
    intBkg = bkg.IntegralAndError(1, bkg.GetNbinsX(), errBkg)
    ratio = intData / intBkg if intBkg!=0 else 0.
    error = math.hypot(errData[0]*ratio/intData,  errBkg[0]*ratio/intBkg) if intData>0 and intBkg>0 else 0
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(62)
    latex.SetTextSize(0.08)
    latex.DrawLatex(0.25, 0.85, "Data/Bkg = %.3f #pm %.3f" % (ratio, error))
    print "  Ratio:\t%.3f +- %.3f" % (ratio, error)
    #return [ratio, error]


def drawStat(data, bkg):
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextFont(62)
    latex.SetTextSize(0.08)
#    chi2 = min(data.Chi2Test(bkg, "UW,CHI2/NDF"), data.Chi2Test(bkg, "WW,CHI2/NDF"))
    chi2 = data.Chi2Test(bkg, "UW,CHI2/NDF")
#    for i in range(bkg.GetNbinsX()):
#        if bkg.GetBinContent(i+1) < 1.e-6: bkg.SetBinError(i+1, 0.)
    latex.DrawLatex(0.55, 0.85, "#chi^{2}/ndf = %.2f,   K-S = %.3f" % (chi2, data.KolmogorovTest(bkg)))

def drawCut(cut, ymin, ymax):
    line = TLine()
    line.SetLineWidth(2)
    line.SetLineStyle(7)
    line.SetLineColor(1)
    line.PaintLineNDC(cut, ymin, cut, ymax)

def setHistStyle(hist, r=1.1):
    hist.GetXaxis().SetTitleSize(hist.GetXaxis().GetTitleSize()*r*r)
    hist.GetYaxis().SetTitleSize(hist.GetYaxis().GetTitleSize()*r*r)
    hist.GetXaxis().SetLabelSize(hist.GetXaxis().GetLabelSize()*r)
    hist.GetYaxis().SetLabelSize(hist.GetYaxis().GetLabelSize()*r)
    hist.GetXaxis().SetLabelOffset(hist.GetXaxis().GetLabelOffset()*r*r*r*r*r*r)
    hist.GetXaxis().SetTitleOffset(hist.GetXaxis().GetTitleOffset()*r)
    hist.GetYaxis().SetTitleOffset(hist.GetYaxis().GetTitleOffset())
    if hist.GetXaxis().GetTitle().find("GeV") != -1: # and not hist.GetXaxis().IsVariableBinSize()
        div = (hist.GetXaxis().GetXmax() - hist.GetXaxis().GetXmin()) / hist.GetXaxis().GetNbins()
        hist.GetYaxis().SetTitle("Events / %.1f GeV" % div)

def addOverflow(hist, addUnder=True):
    n = hist.GetNbinsX()
    hist.SetBinContent(n, hist.GetBinContent(n) + hist.GetBinContent(n+1))
    hist.SetBinError(n, math.sqrt( hist.GetBinError(n)**2 + hist.GetBinError(n+1)**2 ) )
    #hist.SetBinContent(n+1, 0.) # For some reason, this doubles the number of bins sometimes
    #hist.SetBinError(n+1, 0.)
    if addUnder:
        hist.SetBinContent(1, hist.GetBinContent(0) + hist.GetBinContent(1))
        hist.SetBinError(1, math.sqrt( hist.GetBinError(0)**2 + hist.GetBinError(1)**2 ) )
        hist.SetBinContent(0, 0.)
        hist.SetBinError(0, 0.)

def setPad(Pad):
    Pad.SetTopMargin(0.06)
#    Pad.SetBottomMargin(0.05)
    Pad.SetRightMargin(0.05)
    Pad.SetTicks(1, 1)

def setTopPad(TopPad, r=4):
    TopPad.SetPad("TopPad", "", 0., 1./r, 1.0, 1.0, 0, -1, 0)
    TopPad.SetTopMargin(0.24/r)
    TopPad.SetBottomMargin(2*0.04/r)
    TopPad.SetRightMargin(0.05)
    TopPad.SetLeftMargin(0.12)
    TopPad.SetTicks(1, 1)

def setBotPad(BotPad, r=4):
    BotPad.SetPad("BotPad", "", 0., 0., 1.0, 1./r, 0, -1, 0)
    BotPad.SetTopMargin(0.5*r/100.)
    BotPad.SetBottomMargin(r/10.)
    BotPad.SetRightMargin(0.05)
    BotPad.SetLeftMargin(0.12)
    BotPad.SetTicks(1, 1)

def setBotStyle(h, r=4, fixRange=True):
    h.GetXaxis().SetLabelSize(h.GetXaxis().GetLabelSize()*(r-1));
    h.GetXaxis().SetLabelOffset(h.GetXaxis().GetLabelOffset()*(r-1));
    h.GetXaxis().SetTitleSize(h.GetXaxis().GetTitleSize()*(r-1));
    h.GetYaxis().SetLabelSize(h.GetYaxis().GetLabelSize()*(r-1));
    h.GetYaxis().SetNdivisions(505);
    h.GetYaxis().SetTitleSize(h.GetYaxis().GetTitleSize()*(r-1));
    h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset()/(r-1));
    if fixRange:
        h.GetYaxis().SetRangeUser(0., 2.)
        for i in range(1, h.GetNbinsX()+1):
            if h.GetBinContent(i)<1.e-6:
                h.SetBinContent(i, -1.e-6)
    
def drawCut(hist):
    #drawCut(80, 140, 0., hist['BkgSum'].GetMaximum())
    line1 = TLine(80, 0, 80, hist['BkgSum'].GetMaximum())
    line1.SetLineWidth(2)
    line1.SetLineStyle(7)
    line1.SetLineColor(1)
    line1.Draw()
    
    line2 = TLine(140, 0, 140, hist['BkgSum'].GetMaximum())
    line2.SetLineWidth(2)
    line2.SetLineStyle(7)
    line2.SetLineColor(1)
    line2.Draw()
    
    line1 = TLine(0.841, 0, 0.841, 15)
    line1.SetLineWidth(2)
    line1.SetLineStyle(7)
    line1.SetLineColor(1)
    line1.Draw()
    
    line1 = TLine(100, 0, 100, hist['BkgSum'].GetMaximum())
    line1.SetLineWidth(2)
    line1.SetLineStyle(7)
    line1.SetLineColor(1)
    line1.Draw()


