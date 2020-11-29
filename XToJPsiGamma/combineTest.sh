# /bin/bash/

option="--robustFit=1"
#option="--cminDefaultMinimizerStrategy 2"



dir=combineTmp/
cp $1 $dir
name=$(basename $1 .txt)

combine -M FitDiagnostics --datacard datacards/$name.txt --saveShapes --saveWithUncertainties --expectSignal=10 --keepFailures --name _$name $option
mv fitDiagnostics_$name.root $dir
python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py --vtol=0.0000001 -f text $dir/fitDiagnostics_$name.root | sed -e 's/!/ /g' -e 's/,/ /g' | tail -n +2 > $dir/pulls_$name.txt
python pulls.py -b -f $dir/pulls_$name.txt -o $dir/pulls_$name

rm  $dir/$name.txt #$dir/pulls_$name.txt # $dir/fitDiagnostics_$name.root
#rm $dir/impacts_$name.json $dir/$name.root
rm higgsCombine*.root
rm roostats-*
#rm fitDiagnostics*.root

echo -e "\e[00;32mAll clear\e[00m"
