#!/bin/bash

cd datacards/

for signal in ZToJPsiG HToJPsiG
do
    echo Combining cards for $signal ...
    combineCards.py "$signal"_EB="$signal"_EB.txt "$signal"_EE="$signal"_EE.txt > "$signal".txt
done

cd ..

echo -e "\e[00;32mAll clear\e[00m"
