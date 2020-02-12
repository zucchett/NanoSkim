#!/bin/env python

import os, sys
from global_paths import *
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from skimmer import *


import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)

parser.add_option("-l", "--list", action="store", type="string", dest="list", default="")
parser.add_option("-i", "--input", action="store", type="string", dest="input", default="")
parser.add_option("-o", "--output", action="store", type="string", dest="output", default="outputTest/")
parser.add_option("-f", "--filter", action="store", type="string", dest="filter", default=None)
parser.add_option("-y", '--year', action='store', type=int, dest="year", default=0)
parser.add_option("-n", '--max', action='store', type=long, dest="maxEntries", default=1e9)
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
(options, args) = parser.parse_args()



fileList = []
if len(options.input) > 0:
    for f in options.input.split(','):
        if len(f) > 0: fileList += [FILESITE + f]
if len(options.list) > 0:
    with open(options.list, "r") as f:
        for f in f.read().splitlines():
            if len(f) > 0: fileList += [FILESITE + f]



#fileList = ["root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv5/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext2-v1/120000/BD54F09C-7429-9547-A169-467F4AFB9606.root"] #["root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAOD/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/40000/2CE738F9-C212-E811-BD0E-EC0D9A8222CE.root"]
#fileList = ["root://cms-xrd-global.cern.ch//store/mc/RunIIAutumn18NanoAODv5/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/Nano1June2019_102X_upgrade2018_realistic_v19_ext3-v1/20000/8CC8B22B-6E75-F648-97DA-0ACB3AB5DB98.root"]
#fileList = ["root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv5/ZToJPsiGamma-TuneCUETP8M1_13TeV-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v2/20000/7A2A12E7-B35B-2B40-930A-D89F0FCA0F98.root"]
#fileList = ["root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv5/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/100000/FAB838BB-6F66-6B4A-B772-A1B511F28ECB.root"]
#fileList = ["root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv5/QCD_HT100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/70000/9AB2845B-462E-8E42-8605-84606FB59047.root"]
#fileList = ["root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv5/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/70000/A03EC876-43DF-8841-BD98-5E345C766D5C.root"]
#preselection="Jet_pt[0] > 250"
preselection = None
jsonFile = None

if len(fileList) == 0:
    print "- Filelist is empty"
    exit()
elif "Run2016" in fileList[0]: jsonFile = MAINDIR + 'json/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt' # 36.773 /fb
elif "Run2017" in fileList[0]: jsonFile = MAINDIR + 'json/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt' # 41.86 /fb
elif "Run2018" in fileList[0]: jsonFile = MAINDIR + 'json/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt' # 58.83 /fb


p=PostProcessor(outputDir=options.output, inputFiles=fileList, cut=preselection, branchsel=None, modules=[Skimmer()], jsonInput=jsonFile, histFileName=None, histDirName=None, outputbranchsel=MAINDIR + "keep_and_drop.txt", maxEntries=long(options.maxEntries))
#p=PostProcessor(outputDir=options.output, inputFiles=fileList, cut=preselection, branchsel=None, modules=[Skimmer()], histFileName="plotFile.root", histDirName="plots", maxEntries=1000)
p.run()

print "+ Done."


#def __init__(self,outputDir,inputFiles,cut=None,branchsel=None,modules=[],compression="LZMA:9",friend=False,postfix=None,jsonInput=None,noOut=False,justcount=False,provenance=False,haddFileName=None,fwkJobReport=False,histFileName=None,histDirName=None,outputbranchsel=None,maxEntries=None,firstEntry=0,prefetch=False,longTermCache=False):

# voms-proxy-init --voms cms --valid 168:00
