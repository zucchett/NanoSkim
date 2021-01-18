import argparse
import sys
import os
from global_paths import *



################################################################################
# COMMAND-LINE PARSER
################################################################################
parser = argparse.ArgumentParser(description="Submit gridpack generation on lsf")

parser.add_argument('-i', "--input", type=str, dest="ipath", default=MG5DIR,            help="Input folder")
parser.add_argument('-c', "--cards", type=str, dest="cpath", default=CARDDIR,           help="Cards folder wrt genproduction MadGraph path")
parser.add_argument('-w', "--work",  type=str, dest="wpath", default=WORKDIR,           help="Output folder")
parser.add_argument('-q', "--queue", type=str, dest="queue", default="local-cms-short", help="Submission queue")

args = parser.parse_args()
################################################################################



# get command-line arguments...
INPUT_PATH = args.ipath + "/" # safer to add "/" at the end
CARD_PATH  = args.cpath + "/"
WORK_PATH  = args.wpath + "/"
QUEUE      = args.queue

H_prod_list  = ["ggH", "VBF", "WH", "ZH", "ttH", "bbH"]
Z_prod_list  = ["qqZ"]
M_meson_list = ["JPsi", "PsiPrime"]

for prod in H_prod_list:
    for meson in M_meson_list:
        PROC_ID = "HTo" + meson + "G_ToMuMuG_" + prod

        script  = "echo "
        # script in a single line format
        script += "\""
        script += "cd " + INPUT_PATH + "; "
        script += "./gridpack_generation.sh " + PROC_ID + " " + CARD_PATH + PROC_ID + ";"
        script += "\""
        # submission through pipe operator
        script += " | "
        script += "bsub"
        script += " -J " + "HTo" + meson + "G_ToMuMuG_" + prod
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
        script += "cd " + INPUT_PATH + "; "
        script += "./gridpack_generation.sh " + PROC_ID + " " + CARD_PATH + PROC_ID + ";"
        script += "\""
        # submission through pipe operator
        script += " | "
        script += "bsub"
        script += " -J " + "HTo" + meson + "G_ToMuMuG_" + prod
        script += " -oo " + WORK_PATH + "outfile_%J.txt"
        script += " -eo " + WORK_PATH + "errorfile_%J.txt"
        script += " -cwd " + WORK_PATH
        script += " -q " + QUEUE
        # sys.stdout.write(script + "\n\n")
        os.system(script)
