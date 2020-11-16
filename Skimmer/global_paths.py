#! /usr/bin/env python

import os

###
### Auxiliary file defining all global paths for the analysis to work.
###

# CMSSW directory that is used in the ntuple production
CMSSWDIR = os.getenv("CMSSW_BASE") + "/src/"

# version of the NanoAOD to be used and corresponding filelist
FILELIST = "fileList_v7"

# primary work directory where the analysis scripts are located
MAINDIR = CMSSWDIR + "/NanoSkim/Skimmer/"

# local directory to store small output files for further inspection
TESTDIR = "outputTest/"

# large enough storage space to hold the unskimmed primary ntuples produced directly from NanoAOD
OUTDIR = "/lustre/cmswork/" + os.getenv("USER") + "/Skim/Temp/"

# LSF working directory
LSFDIR = CMSSWDIR + "/NanoSkim/Skimmer/LSFWD/"

# location where the HTCondor submission log files (including stderr & stdout) should be located
LOGDIR = CMSSWDIR + "/NanoSkim/Skimmer/LSF/"

# location where the combine tool is installed
COMBINEDIR = CMSSWDIR + "/HiggsAnalysis/CombinedLimit/"

# File prefix to prepend to the file name
#FILESITE = "root://cms-xrd-global.cern.ch/"
#FILESITE = "root://xrootd-cms.infn.it/"
FILESITE = "root://xrootd-cms.infn.it//"
#FILESITE = "dcap://t2-srm-02.lnl.infn.it/pnfs/lnl.infn.it/data/cms/"

# Local file prefix
LOCALSITE = "root://xrootd-cms.infn.it/"

# Python
PYTHONBASE = "/cvmfs/cms.cern.ch/slc7_amd64_gcc700/external/python/2.7.14-omkpbe4"

# Grid user proxy to run on files outside T2
TEMPPROXY = "/tmp/x509up_u723"
USERPROXY = CMSSWDIR + "/NanoSkim/Skimmer/x509up_u723" # this location HAS TO BE on lustre


if __name__ == "__main__":
    from argparse import ArgumentParser 
    parser = ArgumentParser()
    parser.add_argument('-g', '--get',   dest='get', type=str, default='', action='store', help="Global path to return.")
    args = parser.parse_args()

    if args.get != '':
        cmd = "print "+args.get
        try:
            exec cmd
        except NameError:
            print ''
    
