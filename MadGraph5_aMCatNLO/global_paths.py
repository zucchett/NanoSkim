# Auxiliary file defining all global paths for the signal generation studies
import os



# CMSSW directory that is used in the ntuple production
# CMSSWDIR  = os.getenv("CMSSW_BASE") + "/src"

# directory with the .root files with MC events
DATADIR   = "/lustre/cmswork/ardino/MG5_data"

# directory where the plots folder with the features distributions should be saved
PLOTDIR   = "/lustre/cmswork/ardino/MG5_data"

# path of cmssw genproductions
GENDIR    = "/lustre/cmswork/ardino/genproductions"

# path of MadGraph5 folder in cmssw genproductions
MG5DIR    = GENDIR + "/bin/MadGraph5_aMCatNLO"

# working directory when submitting gridpacks and generating from them
WORKDIR   = "/lustre/cmswork/ardino/genproductions/bin/MadGraph5_aMCatNLO/work"

# path to ExRootAnalysis
EXROOTDIR = "/lustre/cmswork/ardino/MG5_aMC_v2_6_5/ExRootAnalysis"

# path to cards relative to MadGraph genproductions
CARDDIR   = "cards/production/13TeV"

# folder with gridpacks in tarball format
GRIDDIR   = "/lustre/cmswork/ardino/genproductions/bin/MadGraph5_aMCatNLO/gridpacks"
