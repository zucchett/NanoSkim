#! /usr/bin/env python

###
### Auxiliary file defining all global paths for the analysis to work.
###

FILELIST = "fileList_v5"

## primary work directory where the analysis scripts are located
MAINDIR = "/lustre/cmswork/zucchett/Skim/CMSSW_10_2_6/src/NanoSkim/Skimmer/"

# local directory to store small output files for further inspection
TESTDIR = "outputTest/"

# large enough storage space to hold the unskimmed primary ntuples produced directly from NanoAOD
OUTDIR = "/lustre/cmswork/zucchett/Skim/Temp/"

# LSF working directory
LSFDIR = "/lustre/cmswork/zucchett/Skim/CMSSW_10_2_6/src/NanoSkim/Skimmer/LSFWD/"

# location where the HTCondor submission log files (including stderr & stdout) should be located
LOGDIR = "/lustre/cmswork/zucchett/Skim/CMSSW_10_2_6/src/NanoSkim/Skimmer/LSF/"

# CMSSW directory that is used in the ntuple production
CMSSWDIR = "/lustre/cmswork/zucchett/Skim/CMSSW_10_2_6/src/"

# location where the combine tool is installed
COMBINEDIR = "/lustre/cmswork/zucchett/Skim/CMSSW_10_2_6/src/HiggsAnalysis/CombinedLimit/"

# File prefix to prepend to the file name
#FILESITE = "root://cms-xrd-global.cern.ch/"
#FILESITE = "root://xrootd-cms.infn.it/"
FILESITE = "root://xrootd-cms.infn.it//"
#FILESITE = "dcap://t2-srm-02.lnl.infn.it/pnfs/lnl.infn.it/data/cms/"

# Local file prefix
LOCALSITE = "root://xrootd-cms.infn.it/"

# Grid user proxy to run on files outside T2
USERPROXY = "/lustre/cmswork/zucchett/Skim/CMSSW_10_2_6/src/NanoSkim/Skimmer/x509up_u723"


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
    
