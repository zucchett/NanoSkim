#/bin/bash

#python pico.py -p
python dijet.py -b -a
source combineCards.sh
combine -M AsymptoticLimits datacards/ZToJPsiG.txt
combine -M AsymptoticLimits datacards/HToJPsiG.txt
combine -M Significance -t -1 --expectSignal=1 datacards/ZToJPsiG.txt
combine -M Significance -t -1 --expectSignal=1 datacards/HToJPsiG.txt

