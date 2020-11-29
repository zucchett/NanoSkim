#!/bin/bash

# How to run:
#  source combineImpacts.sh datacard


option="" #--freezeNuisanceGroups=shape2"
#option="-t -1" # Asimov dataset
#option="--freezeNuisanceGroups=theory"
#option="--freezeNuisanceGroups=theory  --minimizerAlgo=Minuit2 --minimizerStrategy=2"

dir=combineTmp/
cp $1 $dir
name=$(basename $1 .txt)
mass=90 #$(echo $name | tr -dc '0-9')

# To derive Impacts (https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/SWGuideNonStandardCombineUses#Nuisance_parameter_impacts):
text2workspace.py $dir/$name.txt # produces .root file in the same directory of the datacard
combine -M MultiDimFit -n _initialFit_Test --algo singles --redefineSignalPOIs r --robustFit 1 --mass $mass $option -d $dir/$name.root #--rMin -1.0 --rMax 1.0
combineTool.py -M Impacts -d $dir/$name.root --mass $mass --robustFit 1 --doFits --parallel 16 #--rMin -1.0 --rMax 1.0
combineTool.py -M Impacts -d $dir/$name.root --mass $mass -o $dir/impacts_$name.json #--rMin -1.0 --rMax 1.0
plotImpacts.py -i $dir/impacts_$name.json --cms-label Preliminary -o $dir/impacts_$name # --transparent --color-groups 1,8,9,39,2
#pdftoppm -png -f 1 $dir/impacts_$name.pdf $dir/impacts_$name

#text2workspace.py $dir/$name.txt # produces .root file in the same directory of the datacard
#combineTool.py -M Impacts -d $dir/$name.root --mass $mass --doInitialFit --robustFit 1
#combineTool.py -M Impacts -d $dir/$name.root --mass $mass --robustFit 1 --doFits --parallel 32 #--rMin -1.0 --rMax 1.0
#combineTool.py -M Impacts -d $dir/$name.root --mass $mass -o $dir/impacts_$name.json #--rMin -1.0 --rMax 1.0
#plotImpacts.py -i $dir/impacts_$name.json --cms-label Preliminary -o $dir/impacts_$name # --transparent --color-groups 1,8,9,39,2
##pdftoppm -png -f 1 $dir/impacts_$name.pdf $dir/impacts_$name

## Clean
wait

rm  $dir/$name.txt #$dir/pulls_$name.txt # $dir/fitDiagnostics_$name.root
#rm $dir/impacts_$name.json $dir/$name.root
rm higgsCombine*.root
rm roostats-*
#rm fitDiagnostics*.root

echo -e "\e[00;32mAll clear\e[00m"
