import argparse
import sys
import os
from global_paths import *



################################################################################
# COMMAND-LINE PARSER
################################################################################
parser = argparse.ArgumentParser(description="Submit gridpack generation on lsf")

parser.add_argument('-i', "--input",  type=str, dest="ipath", default=GRIDDIR,           help="Input folder")
parser.add_argument('-w', "--work",   type=str, dest="wpath", default=WORKDIR,           help="Work folder")
parser.add_argument('-o', "--output", type=str, dest="opath", default=DATADIR,           help="Output folder")
parser.add_argument('-e', "--exroot", type=str, dest="epath", default=EXROOTDIR,         help="ExRootAnalysis folder")
parser.add_argument('-n', "--nev",    type=int, dest="nev",   default=100000,            help="Number of events to generate")
parser.add_argument('-s', "--seed",   type=int, dest="seed",  default=1234567,           help="Seed")
parser.add_argument('-q', "--queue",  type=str, dest="queue", default="local-cms-short", help="Submission queue")

args = parser.parse_args()
################################################################################



# get command-line arguments...
INPUT_PATH  = args.ipath + "/" # safer to add "/" at the end
WORK_PATH   = args.wpath + "/"
OUTPUT_PATH = args.opath + "/"
EXROOT_PATH = args.epath + "/"
NEVENTS     = args.nev
SEED        = args.seed
QUEUE       = args.queue

H_prod_list  = ["ggH", "VBF", "WH", "ZH", "ttH", "bbH"]
Z_prod_list  = ["qqZ"]
M_meson_list = ["JPsi", "PsiPrime"]

for prod in H_prod_list:
    for meson in M_meson_list:
        PROC_ID = "HTo" + meson + "G_ToMuMuG_" + prod

        script  = "echo "
        # script in a single line format
        script += "\""
        script += "cd /lustre/cmswork/ardino/CMSSW_10_6_9/src/; cmsenv; "
        script += "cd " + WORK_PATH + "; "
        script += "mkdir -p " + PROC_ID + "; "
        script += "cd " + PROC_ID + "; "
        script += "tar -xavf " + INPUT_PATH + PROC_ID + "*.tar.xz" + "; "
        script += "./runcmsgrid.sh " + str(NEVENTS) + " " + str(SEED) + " " + "1" + "; "
        script += EXROOT_PATH + "ExRootLHEFConverter " + "*.lhe " + OUTPUT_PATH + PROC_ID + ".root" + "; "
        script += "\""
        # submission through pipe operator
        script += " | "
        script += "bsub"
        script += " -J " + PROC_ID
        script += " -oo " + WORK_PATH + "outfile_%J.txt"
        script += " -eo " + WORK_PATH + "errorfile_%J.txt"
        script += " -cwd " + WORK_PATH
        script += " -q " + QUEUE
        # sys.stdout.write(script + "\n\n")
        os.system(script)

for prod in Z_prod_list:
    for meson in M_meson_list:
        PROC_ID = "ZTo" + meson + "G_ToMuMuG_" + prod

        script  = "echo "
        # script in a single line format
        script += "\""
        script += "cd /lustre/cmswork/ardino/CMSSW_10_6_9/src/; cmsenv; "
        script += "cd " + WORK_PATH + "; "
        script += "mkdir -p " + PROC_ID + "; "
        script += "cd " + PROC_ID + "; "
        script += "tar -xavf " + INPUT_PATH + PROC_ID + "*.tar.xz" + "; "
        script += "./runcmsgrid.sh " + str(NEVENTS) + " " + str(SEED) + " " + "1" + "; "
        script += EXROOT_PATH + "ExRootLHEFConverter " + "*.lhe " + OUTPUT_PATH + PROC_ID + ".root" + "; "
        script += "\""
        # submission through pipe operator
        script += " | "
        script += "bsub"
        script += " -J " + PROC_ID
        script += " -oo " + WORK_PATH + "outfile_%J.txt"
        script += " -eo " + WORK_PATH + "errorfile_%J.txt"
        script += " -cwd " + WORK_PATH
        script += " -q " + QUEUE
        # sys.stdout.write(script + "\n\n")
        os.system(script)
