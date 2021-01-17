import fileinput
import argparse
import sys
import os



################################################################################
# COMMAND-LINE PARSER
################################################################################
parser = argparse.ArgumentParser(description="Modify path of MadGraph model in *_proc_card.dat")

parser.add_argument('-p', "--path",   type=str, dest="MPATH", default="", help="Path of MadGraph model")
parser.add_argument('-i', "--input",  type=str, dest="IPATH",             help="Input folder with cards")

args = parser.parse_args()
################################################################################



def replace_path(file, token, path):
    for line in fileinput.input(file, inplace=1):
        if token in line:
            line = "import model " + path + "JPsi_UFO_with_Z__hgg_plugin\n"
        sys.stdout.write(line)



# get command-line arguments...
CARDS_PATH = args.IPATH + "/" # safer to add "/" at the end
if args.MPATH!="":
    MODEL_PATH = args.MPATH + "/"
else:
    MODEL_PATH = args.MPATH



for dir in os.listdir(CARDS_PATH):
    file = "./cards/" + dir + "/" + dir + "_proc_card.dat"
    sys.stdout.write("./cards/" + dir + "/" + dir + "_proc_card.dat" + "\n")
    replace_path(file, "JPsi_UFO_with_Z__hgg_plugin", MODEL_PATH)
