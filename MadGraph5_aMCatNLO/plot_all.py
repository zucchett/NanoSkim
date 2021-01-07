import argparse
import sys
import os



################################################################################
# COMMAND-LINE PARSER
################################################################################
parser = argparse.ArgumentParser(description="Plot all MadGraph5_aMCatNLO results")

parser.add_argument('-i', "--input",  type=str, dest="ipath", default="/lustre/cmswork/ardino/MG5_data/", help="Input folder")
parser.add_argument('-o', "--output", type=str, dest="opath", default="/lustre/cmswork/ardino/MG5_data/", help="Output folder")

args = parser.parse_args()
################################################################################



# stuff
RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"

# get command-line arguments...
INPUT_PATH  = args.ipath + "/" # safer to add "/" at the end
OUTPUT_PATH = args.opath + "/" # safer to add "/" at the end

H_prod_list = ["ggH", "VBF", "WH", "ZH", "ttH", "bbH"]
Z_prod_list = ["qqZ"]

for prod in H_prod_list:
    sys.stdout.write("Processing production mode: " + BOLD + RED + prod + RESET + "\n")
    os.system("python plot_channel.py -b -s H -p " + prod + " -i " + INPUT_PATH + " -o " + OUTPUT_PATH)

for prod in Z_prod_list:
    sys.stdout.write("Processing production mode: " + BOLD + RED + prod + RESET + "\n")
    os.system("python plot_channel.py -b -s Z -p " + prod + " -i " + INPUT_PATH + " -o " + OUTPUT_PATH)
