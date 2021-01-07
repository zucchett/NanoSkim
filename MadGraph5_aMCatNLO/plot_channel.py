import argparse
import sys
import os

import ROOT
from ROOT import gROOT
from ROOT import gStyle, kBlue
from ROOT import TFile, TCanvas
from ROOT import TH1D
from ROOT import TTreeReader, TTreeReaderArray
from ROOT import TLorentzVector


################################################################################
# COMMAND-LINE PARSER
################################################################################
parser = argparse.ArgumentParser(description="Plot MadGraph5_aMCatNLO results")

parser.add_argument('-b', "--batch",  dest="batch", action="store_true", default=False, help="Enable batch mode")
parser.add_argument("-s", "--signal", type=str, dest="S", help="Z/H boson decay")
parser.add_argument('-p', "--pmode",  type=str, dest="P", help="Production mode [ggH, VBF, WH, ZH, ttH, bbH, qqZ]")
parser.add_argument('-i', "--input",  type=str, dest="ipath", default="/lustre/cmswork/ardino/MG5_data/", help="Input folder")
parser.add_argument('-o', "--output", type=str, dest="opath", default="/lustre/cmswork/ardino/MG5_data/", help="Output folder")

args = parser.parse_args()
################################################################################





################################################################################
# PARAMETERS AND PRELIMINARY CHECKS
################################################################################
# parameters
nbins    = 50
patience = 1000
eps      = 1e-6
# ranges for the plots
c_min = -1.0
c_max =  1.0
m_min = {"Z":  80.0, "H": 124.95, "JPsi": 3.094}
m_max = {"Z": 100.0, "H": 125.05, "JPsi": 3.100}
# useful lists with signal and production modes
p_ids  = {"Z": 23, "H": 25}
P_list = ["ggH", "VBF", "WH", "ZH", "ttH", "bbH", "qqZ"]
S_list = ["Z", "H"]

# get command-line arguments...
BATCH_MODE  = args.batch
INPUT_PATH  = args.ipath + "/" # safer to add "/" at the end
OUTPUT_PATH = args.opath + "/" # safer to add "/" at the end
S           = args.S
P           = args.P

# ...and check if what inserted makes sense, otherwise exit
if (S not in S_list):
    sys.stdout.write("Wrong signal type inserted")
    sys.exit()
elif (P not in P_list):
    sys.stdout.write("Wrong production mode inserted")
    sys.exit()
else:
    pass

if BATCH_MODE:
    gROOT.SetBatch(True)
    gROOT.ProcessLine( "gErrorIgnoreLevel = 2001;")
################################################################################





################################################################################
# READ DATA
# COMPUTE QUANTITIES OF INTEREST EVENT PER EVENT
################################################################################
# open file
file = TFile.Open(INPUT_PATH + S + "ToJPsiG_ToMuMuG_" + P + ".root")

# read branches using TTreeReader and TTreeReaderArray
rLHE  = TTreeReader("LHEF", file)
p_nev = TTreeReaderArray(ROOT.Int_t)   (rLHE, "Event.Nparticles")
p_ID  = TTreeReaderArray(ROOT.Int_t)   (rLHE, "Particle.PID")
p_pt  = TTreeReaderArray(ROOT.Double_t)(rLHE, "Particle.PT" )
p_eta = TTreeReaderArray(ROOT.Double_t)(rLHE, "Particle.Eta")
p_phi = TTreeReaderArray(ROOT.Double_t)(rLHE, "Particle.Phi")
p_M   = TTreeReaderArray(ROOT.Double_t)(rLHE, "Particle.M"  )
p_px  = TTreeReaderArray(ROOT.Double_t)(rLHE, "Particle.Px" )
p_py  = TTreeReaderArray(ROOT.Double_t)(rLHE, "Particle.Py" )
p_pz  = TTreeReaderArray(ROOT.Double_t)(rLHE, "Particle.Pz" )
p_E   = TTreeReaderArray(ROOT.Double_t)(rLHE, "Particle.E"  )

# Loop over all entries of the TTree or TChain.
# define number of particles for each cathegory
n_x  = 0
n_g  = 0
n_j  = 0
n_mm = 0
n_mp = 0
# map index to particle
i_x  = 0
i_g  = 0
i_j  = 0
i_mm = 0
i_mp = 0
# quantities
cosTheta1 = 0.0
tot_ev    = 0

l_cosThetaStar  = []
l_cosTheta1mu_p = []
l_cosTheta1mu_m = []
l_M_mumu        = []
l_M_mumugamma   = []

while (rLHE.Next()):
    if (tot_ev%patience==0):
        if not BATCH_MODE: sys.stdout.write("\rEvents analyzed: "+str(tot_ev))
    # select plausible events
    n_x  = 0;
    n_g  = 0;
    n_j  = 0;
    n_mm = 0;
    n_mp = 0;
    for i in range(p_nev[0]):
        if (p_ID[i]==p_ids[S]) : n_x  += 1;
        if (p_ID[i]==22)       : n_g  += 1;
        if (p_ID[i]==443)      : n_j  += 1;
        if (p_ID[i]==13)       : n_mm += 1;
        if (p_ID[i]==-13)      : n_mp += 1;

    if ((n_x!=1) and (n_g!=1) and (n_j!=1) and (n_mm!=1) and (n_mp!=1)):
        break;

    # map index
    for i in range(p_nev[0]):
        if (p_ID[i]==p_ids[S]) : i_x  = i;
        if (p_ID[i]==22)       : i_g  = i;
        if (p_ID[i]==443)      : i_j  = i;
        if (p_ID[i]==13)       : i_mm = i;
        if (p_ID[i]==-13)      : i_mp = i;

    # define TLorentzVector objects
    # mu_m      : muon (negative charge)
    # mu_p      : antimuon (positive charge)
    # g         : gamma
    # jpsi      : jpsi
    # jpsi_copy : copy of jpsi TLorentzVector
    # x         : heavy boson
    mu_m      = TLorentzVector()
    mu_p      = TLorentzVector()
    g         = TLorentzVector()
    jpsi      = TLorentzVector()
    x         = TLorentzVector()

    # set
    mu_m.SetPtEtaPhiM(p_pt[i_mm], p_eta[i_mm], p_phi[i_mm], p_M[i_mm]);
    mu_p.SetPtEtaPhiM(p_pt[i_mp], p_eta[i_mp], p_phi[i_mp], p_M[i_mp]);
    g.SetPtEtaPhiM   (p_pt[i_g],  p_eta[i_g],  p_phi[i_g],  p_M[i_g] );

    jpsi = mu_m + mu_p
    x    = mu_m + mu_p + g

    mu_m.Boost(-x.BoostVector());
    mu_p.Boost(-x.BoostVector());
    g.Boost   (-x.BoostVector());
    jpsi.Boost(-x.BoostVector());
    x.Boost   (-x.BoostVector());

    mu_m.Boost(-jpsi.BoostVector());
    mu_p.Boost(-jpsi.BoostVector());
    g.Boost   (-jpsi.BoostVector());

    # if ((jpsi.Vect().Mag()>tol) and (mu_p.Vect().Mag()>tol) and (mu_m.Vect().Mag()>tol) and (g.Vect().Mag()>tol) and (x.Vect().Mag()>0)):
    l_cosThetaStar.append(jpsi.CosTheta())

    cosTheta1 = jpsi.Vect().Dot(mu_p.Vect()) / ((jpsi.Vect().Mag())*(mu_p.Vect().Mag()));
    l_cosTheta1mu_p.append(cosTheta1)

    cosTheta1 = jpsi.Vect().Dot(mu_m.Vect()) / ((jpsi.Vect().Mag())*(mu_m.Vect().Mag()));
    l_cosTheta1mu_m.append(cosTheta1)

    M_mumu = (mu_m+mu_p).M()
    l_M_mumu.append(M_mumu)

    M_mumugamma = (mu_m+mu_p+g).M()
    l_M_mumugamma.append(M_mumugamma)

    tot_ev += 1

if not BATCH_MODE: sys.stdout.write("\nCompleted\n")
################################################################################





################################################################################
# PLOT AND SAVE DISTRIBUTIONS
################################################################################
PROC_ID = S + "ToJPsiG_ToMuMuG_" + P
h1 = TH1D("h1", "#bf{" + PROC_ID + "}: cos(#theta_{J/#psi}*) distribution",                     nbins, c_min, c_max);
h2 = TH1D("h2", "#bf{" + PROC_ID + "}: cos(#theta_{J/#psi,#mu^{#scale[1.5]{+}}}) distribution", nbins, c_min, c_max);
h3 = TH1D("h3", "#bf{" + PROC_ID + "}: cos(#theta_{J/#psi,#mu^{#scale[1.5]{-}}}) distribution", nbins, c_min, c_max);
h4 = TH1D("h4", "#bf{" + PROC_ID + "}: m_{#mu#mu} distribution",                                nbins, m_min["JPsi"], m_max["JPsi"]);
h5 = TH1D("h5", "#bf{" + PROC_ID + "}: m_{#mu#mu#gamma} distribution",                          nbins, m_min[S], m_max[S]);

# fill histograms
for i in range(len(l_cosThetaStar)):
    h1.Fill(l_cosThetaStar[i])
    h2.Fill(l_cosTheta1mu_p[i])
    h3.Fill(l_cosTheta1mu_m[i])
    h4.Fill(l_M_mumu[i])
    h5.Fill(l_M_mumugamma[i])

# compute normalizations
y_max_1 = h1.GetMaximum() / (h1.GetBinWidth(1) * h1.Integral())
y_max_2 = h2.GetMaximum() / (h2.GetBinWidth(1) * h2.Integral())
y_max_3 = h3.GetMaximum() / (h3.GetBinWidth(1) * h3.Integral())
y_max_4 = h4.GetMaximum() / (h4.GetBinWidth(1) * h4.Integral())
y_max_5 = h5.GetMaximum() / (h5.GetBinWidth(1) * h5.Integral())

# create directories for plots
SAVE_PATH_S   = OUTPUT_PATH + "plots/"
SAVE_PATH_SP  = OUTPUT_PATH + "plots/" + S + "ToJPsiG_ToMuMuG_" + P + "/"
SAVE_FILENAME = S + "ToJPsiG_ToMuMuG_" + P
if not os.path.isdir(SAVE_PATH_S):
    os.system("mkdir " + SAVE_PATH_S)
if not os.path.isdir(SAVE_PATH_SP):
    os.system("mkdir " + SAVE_PATH_SP)

# plot cosTheta*
c1 = TCanvas("c1", "c1", 800, 600);
h1.GetXaxis().SetTitle("cos(#theta_{J/#psi}*)");
h1.GetYaxis().SetTitle("Density");
h1.GetXaxis().SetDecimals();
h1.GetYaxis().SetDecimals();
h1.SetLineWidth(2)
h1.SetFillStyle(3003)
h1.SetFillColor(9)
gStyle.SetOptStat(0);
h1.Scale(1/(h1.GetBinWidth(1) * h1.Integral()))
h1.GetYaxis().SetRangeUser(0, 1.5*y_max_1);
h1.Draw("HIST");
c1.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_cosThetaStar.png")
c1.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_cosThetaStar.pdf")
c1.Draw()

# plot cosTheta1 (jpsi-mu-)
c2 = TCanvas("c2", "c2", 800, 600);
h2.GetXaxis().SetTitle("cos(#theta_{J/#psi,#mu^{#scale[1.5]{+}}})")
h2.GetYaxis().SetTitle("Density");
h2.GetXaxis().SetDecimals();
h2.GetYaxis().SetDecimals();
h2.SetLineWidth(2)
h2.SetFillStyle(3003)
h2.SetFillColor(9)
gStyle.SetOptStat(0);
h2.Scale(1/(h2.GetBinWidth(1) * h2.Integral()))
h2.GetYaxis().SetRangeUser(0, 1.5*y_max_2);
h2.Draw("HIST");
c2.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_cosTheta1_mu_p.png")
c2.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_cosTheta1_mu_p.pdf")
c2.Draw()

# plot cosTheta1 (jpsi-mu+)
c3 = TCanvas("c3", "c3", 800, 600);
h3.GetXaxis().SetTitle("cos(#theta_{J/#psi,#mu^{#scale[1.5]{-}}})")
h3.GetYaxis().SetTitle("Density");
h3.GetXaxis().SetDecimals();
h3.GetYaxis().SetDecimals();
h3.SetLineWidth(2)
h3.SetFillStyle(3003)
h3.SetFillColor(9)
gStyle.SetOptStat(0);
h3.Scale(1/(h3.GetBinWidth(1) * h3.Integral()))
h3.GetYaxis().SetRangeUser(0, 1.5*y_max_3);
h3.Draw("HIST");
c3.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_cosTheta1_mu_m.png")
c3.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_cosTheta1_mu_m.pdf")
c3.Draw()

# plot m_{mumu}
c4 = TCanvas("c4", "c4", 800, 600);
h4.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
h4.GetYaxis().SetTitle("Density");
h4.GetXaxis().SetDecimals();
h4.GetYaxis().SetDecimals();
h4.SetLineWidth(2)
h4.SetFillStyle(3003)
h4.SetFillColor(9)
gStyle.SetOptStat(0);
h4.Scale(1/(h4.GetBinWidth(1) * h4.Integral()))
h4.GetYaxis().SetRangeUser(0, 1.5*y_max_4);
h4.Draw("HIST");
c4.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_m_mumu.png")
c4.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_m_mumu.pdf")
c4.Draw()

# plot m_{mumugamma}
c5 = TCanvas("c5", "c5", 800, 600);
h5.GetXaxis().SetTitle("m_{#mu#mu#gamma} [GeV]")
h5.GetYaxis().SetTitle("Density");
h5.GetXaxis().SetDecimals();
h5.GetYaxis().SetDecimals();
h5.SetLineWidth(2)
h5.SetFillStyle(3003)
h5.SetFillColor(9)
gStyle.SetOptStat(0);
h5.Scale(1/(h5.GetBinWidth(1) * h5.Integral()))
h5.GetYaxis().SetRangeUser(0, 1.5*y_max_5);
h5.Draw("HIST");
c5.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_m_mumugamma.png")
c5.SaveAs(SAVE_PATH_SP + SAVE_FILENAME + "_m_mumugamma.pdf")
c5.Draw()
################################################################################
