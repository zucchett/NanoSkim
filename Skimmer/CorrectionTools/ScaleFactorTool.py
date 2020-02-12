#! /bin/usr/env bash
# Author: Izaak Neutelings (November 2018)
import os, re
from ROOT import TFile, TH2F #, TH2F, TGraphAsymmErrors, Double()
import numpy as np

def ensureTFile(filename,option='READ'):
  """Open TFile, checking if the file in the given path exists."""
  if not os.path.isfile(filename):
    print '>>> ERROR! ScaleFactorTool.ensureTFile: File in path "%s" does not exist!!'%(filename)
    exit(1)
  file = TFile(filename,option)
  if not file or file.IsZombie():
    print '>>> ERROR! ScaleFactorTool.ensureTFile Could not open file by name "%s"'%(filename)
    exit(1)
  return file
  


class ScaleFactor:
    
    def __init__(self, filename, histname, name="<noname>", ptvseta=True):
        #print '>>> ScaleFactor.init("%s","%s",name="%s",ptvseta=%r)'%(filename,histname,name,ptvseta)
        self.name     = name
        self.ptvseta  = ptvseta
        self.filename = filename
        self.file     = ensureTFile(filename)
        self.hist     = self.file.Get(histname)
        if not self.hist:
          print '>>> ScaleFactor(%s).__init__: histogram "%s" does not exist in "%s"'%(self.name,histname,filename)
          exit(1)
        self.hist.SetDirectory(0)
        self.file.Close()
        
        if ptvseta: 
          self.getSF = self.getSF_ptvseta
          self.getSFerror = self.getSFerror_ptvseta
        else:       
          self.getSF = self.getSF_etavspt
          self.getSFerror = self.getSFerror_etavspt
        
    def getSF_ptvseta(self, pt, eta):
        """Get SF for a given pT, eta."""
        xbin = self.hist.GetXaxis().FindBin(eta)
        ybin = self.hist.GetYaxis().FindBin(pt)
        if xbin==0: xbin = 1
        elif xbin>self.hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>self.hist.GetYaxis().GetNbins(): ybin -= 1
        sf   = self.hist.GetBinContent(xbin,ybin)
        if sf==0: sf=1
        return sf
    
    def getSFerror_ptvseta(self, pt, eta):
        """Get SF for a given pT, eta."""
        xbin = self.hist.GetXaxis().FindBin(eta)
        ybin = self.hist.GetYaxis().FindBin(pt)
        if xbin==0: xbin = 1
        elif xbin>self.hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>self.hist.GetYaxis().GetNbins(): ybin -= 1
        error = self.hist.GetBinError(xbin,ybin)
        return error

    
    def getSF_etavspt(self, pt, eta):
        """Get SF for a given pT, eta."""
        xbin = self.hist.GetXaxis().FindBin(pt)
        ybin = self.hist.GetYaxis().FindBin(eta)
        if xbin==0: xbin = 1
        elif xbin>self.hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>self.hist.GetYaxis().GetNbins(): ybin -= 1
        sf   = self.hist.GetBinContent(xbin,ybin)
        if sf==0: sf=1
        return sf

    def getSFerror_etavspt(self, pt, eta):
        """Get SF for a given pT, eta."""
        xbin = self.hist.GetXaxis().FindBin(pt)
        ybin = self.hist.GetYaxis().FindBin(eta)
        if xbin==0: xbin = 1
        elif xbin>self.hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>self.hist.GetYaxis().GetNbins(): ybin -= 1
        error = self.hist.GetBinError(xbin,ybin)
        return error

class ScaleFactorCalc:
    
    def __init__(self, filename1, histname1, name1, filename2, histname2, name2, ptvseta=True):
        self.ptvseta  = ptvseta
        self.name1     = name1
        self.filename1 = filename1
        self.file1     = ensureTFile(filename1)
        self.hist1     = self.file1.Get(histname1)
        self.name2     = name2
        self.filename2 = filename2
        self.file2     = ensureTFile(filename2)
        self.hist2     = self.file2.Get(histname2)
        if not self.hist1:
          print '>>> ScaleFactor(%s).__init__: histogram "%s" does not exist in "%s"'%(self.name1,histname1,filename1)
          exit(1)
        if not self.hist2:
          print '>>> ScaleFactor(%s).__init__: histogram "%s" does not exist in "%s"'%(self.name2,histname2,filename2)
          exit(1)
        self.hist1.Divide(self.hist2)
        self.hist = self.hist1
        self.hist.SetDirectory(0)
        self.file1.Close()
        self.file2.Close()
        
        if ptvseta: 
          self.getSF = self.getSF_ptvseta
          self.getSFerror = self.getSFerror_ptvseta
        else:       
          self.getSF = self.getSF_etavspt
          self.getSFerror = self.getSFerror_etavspt
        
    def getSF_ptvseta(self, pt, eta):
        """Get SF for a given pT, eta."""
        xbin = self.hist.GetXaxis().FindBin(eta)
        ybin = self.hist.GetYaxis().FindBin(pt)
        if xbin==0: xbin = 1
        elif xbin>self.hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>self.hist.GetYaxis().GetNbins(): ybin -= 1
        sf   = self.hist.GetBinContent(xbin,ybin)
        if sf==0: sf=1
        return sf
    
    def getSFerror_ptvseta(self, pt, eta):
        """Get SF for a given pT, eta."""
        xbin = self.hist.GetXaxis().FindBin(eta)
        ybin = self.hist.GetYaxis().FindBin(pt)
        if xbin==0: xbin = 1
        elif xbin>self.hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>self.hist.GetYaxis().GetNbins(): ybin -= 1
        error = self.hist.GetBinError(xbin,ybin)
        return error

    
    def getSF_etavspt(self, pt, eta):
        """Get SF for a given pT, eta."""
        xbin = self.hist.GetXaxis().FindBin(pt)
        ybin = self.hist.GetYaxis().FindBin(eta)
        if xbin==0: xbin = 1
        elif xbin>self.hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>self.hist.GetYaxis().GetNbins(): ybin -= 1
        sf   = self.hist.GetBinContent(xbin,ybin)
        if sf==0: sf=1
        return sf

    def getSFerror_etavspt(self, pt, eta):
        """Get SF for a given pT, eta."""
        xbin = self.hist.GetXaxis().FindBin(pt)
        ybin = self.hist.GetYaxis().FindBin(eta)
        if xbin==0: xbin = 1
        elif xbin>self.hist.GetXaxis().GetNbins(): xbin -= 1
        if ybin==0: ybin = 1
        elif ybin>self.hist.GetYaxis().GetNbins(): ybin -= 1
        error = self.hist.GetBinError(xbin,ybin)
        return error

##etaLt = re.compile(r"EtaLt(\dp\d+)")
##etaTo = re.compile(r"Eta(\dp\d+to\dp\d+)")
##etaGt = re.compile(r"EtaGt(\dp\d+)")
#def getEtaRangeFromString(eta):
#    """Get eta range from string."""
#    etainf = 7.0
#    match  = re.match(r"EtaLt(\dp\d+)",eta)
#    if match:
#      return (0,float(match.group(1).replace('p','.')))
#    match = re.match(r"Eta(\dp\d+)to(\dp\d+)",eta)
#    if match:
#      return (float(match.group(1).replace('p','.')),float(match.group(2).replace('p','.')))
#    match = re.match(r"EtaGt(\dp\d+)",eta)
#    if match:
#      return (float(match.group(1).replace('p','.')),etainf)
#    print "ERROR! getEtaRange: Could not find a eta range pattern for the string '%s'"%(eta)
#    return None

#def getBinsFromTGraph(graph):
#    """Get xbins from TGraph."""
#    x, y  = Double(), Double()
#    xlast  = None
#    xbins = [ ]
#    for i in range(0,graph.GetN()):
#      graph.GetPoint(i,x,y)
#      xlow = float(x) - graph.GetErrorXlow(i)
#      xup  = float(x) + graph.GetErrorXhigh(i)
#      if xlow>=xup:
#        print 'Warning! getBinsFromTGraph: Point i=%d of graph "%s": lower x value %.1f >= upper x value %.1f.'%(i,graph.GetName(),xlow,xup)
#      if xlast!=None and abs(xlast-xlow)>1e-5:
#        print 'Warning! getBinsFromTGraph: Point i=%d of graph "%s": lower x value %.1f does not conincide with upper x value of last point, %.1f.'%(i,graph.GetName(),xlow,xlast)
#      xbins.append(xlow)
#      xlast = xup
#    xbins.append(xlast)
#    return xbins
