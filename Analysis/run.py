#! /usr/bin/env python

import os, multiprocessing, math, datetime
from array import array
from ROOT import TFile, TH1, TF1, TLorentzVector, TObject

from samples import sample
from variables import variable
from aliases import alias
from plotUtils import *
from loop import *

import optparse
usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-o', '--output', action='store', type='string', dest='output', default='output.root')
parser.add_option('-p', '--parallelize', action='store_true', dest='parallelize', default=False)
parser.add_option('-r', '--reduce', action='store', type='int', dest='reduce', default=0)
parser.add_option('-y', '--year', action='store', type='int', dest='year', default=0)
parser.add_option('-t', '--tmpdir', action='store', type='string', dest='tmpdir', default='tmp')
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)

(options, args) = parser.parse_args()

output      = options.output.replace(".root", "_%d.root" % options.year if not options.year==0 else ".root")
splitjobs   = options.parallelize
reduction   = max(1, int(options.reduce))
year        = options.year
tmpdir      = options.tmpdir + ("_%d" % options.year if not options.year==0 else "")
verbose     = options.verbose if not splitjobs else False

########## ######## ##########

# Run on a single file
def run(s, ss, filename):
    # Define and initialize histograms
    hist = {}
    for c in variables.keys():
        hist[c] = {}
        for v in variables[c]:
            hist[c][v] = {}
            hist[c][v] = TH1F(c + "_" + v + "_" + s + "_" + filename, ";"+variable[v]['title']+";Events;"+('logx' if variable[v]['logx'] else '')+('logy' if variable[v]['logy'] else ''), variable[v]['nbins'], variable[v]['min'], variable[v]['max'])
            if variable[v]['nbins'] <= 0: hist[c][v] = TH1F(s, ";"+variable[v]['title']+";Events;"+('logx' if variable[v]['logx'] else '')+('logy' if variable[v]['logy'] else ''), len(variable[v]['bins'])-1, array('f', variable[v]['bins']))
            hist[c][v].Sumw2()
            hist[c][v].SetFillColor(sample[s]['fillcolor'])
            hist[c][v].SetFillStyle(sample[s]['fillstyle'])
            hist[c][v].SetLineColor(sample[s]['linecolor'])
            hist[c][v].SetLineStyle(sample[s]['linestyle'])
            hist[c][v].SetDirectory(0)
    
    # Open file and get tree
    inFile = TFile(NTUPLEDIR + '/' + ss + '/' + filename, "READ")
    tree = inFile.Get("Events")
    red = reduction if not "Run201" in ss else 1
    loop(hist, tree, ss, red)
    inFile.Close()
    
    # Create output directories
    if not os.path.isdir(tmpdir): os.mkdir(tmpdir)
    if not os.path.isdir(tmpdir + '/' + ss): os.mkdir(tmpdir + '/' + ss)
    # Write output to file
    outFile = TFile(tmpdir + '/' + ss + '/' + filename, "RECREATE")
    outFile.cd()
    for c in variables.keys():
        if not outFile.GetDirectory(c): outFile.mkdir(c)
        outFile.cd(c)
        for v in variables[c]:
            var = v.replace('[', '_').replace(']', '')
            if not outFile.GetDirectory(var): outFile.mkdir(c + '/' + var)
            outFile.cd(c + '/' + var)
            hist[c][v].Write(s)
    outFile.Close()


def merge(ss):
    os.system("hadd -f " + tmpdir + '/' + ss + ".root " + tmpdir + '/' + ss + "/*.root > /dev/null")
    return


if __name__ == "__main__":
    print "+ Job started [", datetime.datetime.now().time(), "]"
    if not reduction in [0, 1]: print "+ Running with MC reduction factor of", reduction
    ncpu = multiprocessing.cpu_count() - 4 # Leave 4 CPU free
    if splitjobs: print "+ Splitting jobs over", ncpu, "cores..."
    pool = multiprocessing.Pool(processes = ncpu)
    # Loop on samples
    for s in data+back+sign:
        if verbose: print "Sample", ' '*33, 'File', ' '*7, 'Events', ' '*5, '\n', '-'*50
        # Loop on subsamples
        for j, ss in enumerate(sample[s]['files']):
            for f in os.listdir(NTUPLEDIR + '/' + ss):
                if not f.endswith(".root"): continue
                if year == 2016 and not ('Run2016' in ss or 'Summer16' in ss): continue
                if year == 2017 and not ('Run2017' in ss or 'Fall17' in ss): continue
                if year == 2018 and not ('Run2018' in ss or 'Autumn18' in ss): continue
                if not splitjobs: run(s, ss, f)
                else: pool.apply_async(run, args=(s, ss, f, ))
                #hget = result.get()
                if verbose: print ' + ', ss[:25], ' '*10, len(sample[s]['files']), ' '*10

    # Wait for all jobs to finish
    pool.close()
    pool.join()
    print "+ Jobs completed [", datetime.datetime.now().time(), "]"
    
    # Check that output is non-null
#    dirList = os.system("ls " + tmpdir + "/*/*.root")
#    if dirList == 0:
#        print "- Output is empty, check loop code for crashes"
#        exit()
    
    # Merge outputs
    print "+ Micro-merging..."
    poolMerger = multiprocessing.Pool(processes = ncpu)
    for s in data+back+sign:
        for j, ss in enumerate(sample[s]['files']):
            if year == 2016 and not ('Run2016' in ss or 'Summer16' in ss): continue
            if year == 2017 and not ('Run2017' in ss or 'Fall17' in ss): continue
            if year == 2018 and not ('Run2018' in ss or 'Autumn18' in ss): continue
            if not splitjobs: merge(ss)
            else: poolMerger.apply_async(merge, args=(ss,))
    # Wait for micro-merging jobs to finish
    poolMerger.close()
    poolMerger.join()
    
    print "+ Macro-merging [",  datetime.datetime.now().time(), "]"
    os.system("hadd -f " + output + " " + tmpdir + "/*.root > /dev/null")

    print "+ Cleaning up [",  datetime.datetime.now().time(), "]"
    os.system("rm -rf " + tmpdir)

    print "+ Job ended [", datetime.datetime.now().time(), "]"
    
    if year != 0:
        print "+ The output is separated by year. After all jobs are finished, they can be merged in a single file by running the following command:"
        print "hadd -f " + output.replace("_%d" % year, "") + " " + output.replace("_%d" % year, "").replace(".root", "") + "_*.root"
    
    print '+ Done.'

