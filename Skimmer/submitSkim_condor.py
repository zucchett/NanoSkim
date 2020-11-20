#!/bin/env python                                                                                                                                              

# this script will submit skim.py using HTcondor con lxplus. 
# IMPORTANT: make sure you specified a correct path for MAINDIR, LOGDIR, outputDir in global_path.py
# you will be able to check the status of your jobs accessing the .log, .err, .out, .src files automatically created inside LOGDIR.
# make sure LOGDIR and outputDir are clear before running

import os, sys
from global_paths import *
from utils import *

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)

parser.add_option("-f", "--filter", action="store", type="string", dest="filter", default="", help="Specify a string to filter the datasets")
parser.add_option("-y", "--year", action="store", type="string", dest="year", default="", help="Filter datasets according to the year")
parser.add_option("-l", "--local", action="store_true", dest="local", default=False, help="Submit as local jobs")
parser.add_option("-n", "--nFilesPerJob", action="store", type=int, dest="nfiles", default=10, help="Set number of files per job")
parser.add_option("-t", "--test", action="store_true", dest="test", default=False, help="Test run, executes the script but does not submit jobs")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Increase verbosity")
(options, args) = parser.parse_args()


# Make the proxy visible on condor nodes if you need to run on CMS DAS data
# Before running you should make your certificate visible. 
# (see option 3 in  https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRABPrepareLocal#Grid_Proxy)
#
# 1. mkdir -p $HOME/tmp
#
# 2. put your grid proxy in your home area with the following line in your login file:
#      for .cshrc: setenv X509_USER_PROXY $HOME/tmp/x509up
#      for .bashrc: export X509_USER_PROXY=$HOME/tmp/x509up
#   (then log out and log in again and do voms-proxy-init ....)
#
# 3. [put this in your JDL (already included in this script!)]
#      x509userproxy = $ENV(X509_USER_PROXY)
#      use_x509userproxy = True                                                                                
                                                                                         


def runFileLSF(s):
    outputDir = OUTDIR + "/" + s + "/"
    #if not options.test: os.system("rm -rf " + outputDir)                                                                                                     
    with open(FILELIST + "/" + s + ".txt", "r") as f:
        i = 0
        flist = ""
        lines = f.read().splitlines()
        i, last = 0, len(lines)
        for f in lines:
            if len(f) == 0: continue
            flist += f + ','
            if (i > 0 and i % options.nfiles == 0) or i == last-1:
                                                                           
                if options.local:
                    command = "python skim.py -i " + flist + " -o " + outputDir + " &> " + LOGDIR + "/localfile_" + s + ".txt &"
                    if not options.test:
                        os.system(command)
                    elif options.verbose: print "\n", command, "\n"
                else:
                    # src file                                                                                                                                 
                    script_src = open("%s/%s.src" %(LOGDIR, s+'_'+str(i)) , 'w')
                    script_src.write("#!/bin/bash\n")
                    script_src.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
                    script_src.write("cd %s\n"%(CMSSWDIR))
                    script_src.write("eval `scramv1 runtime -sh`\n")#"cmsenv\n")  # explicit command for "cmsenv"                                                                      
                    script_src.write("python "+ MAINDIR + "/skim.py -i " + flist + " -o " + outputDir)
                    script_src.close()
                    os.system("chmod a+x %s/%s.src" %(LOGDIR, s+'_'+str(i)))
                    
                    # condor file                                                                                                                              
                    script_condor = open("%s/%s.condor" %(LOGDIR, s+'_'+str(i)) , 'w')
                    script_condor.write("executable = %s/%s.src\n" %(LOGDIR, s+'_'+str(i)))
                    script_condor.write("universe = vanilla\n")
                    script_condor.write("output = %s/%s.out\n" %(LOGDIR, s+'_'+str(i)))
                    script_condor.write("error =  %s/%s.err\n" %(LOGDIR, s+'_'+str(i)))
                    script_condor.write("log = %s/%s.log\n" %(LOGDIR, s+'_'+str(i)))
                    script_condor.write("x509userproxy = $ENV(X509_USER_PROXY)\n")
                    script_condor.write("use_x509userproxy = True\n")
                    script_condor.write("+MaxRuntime = 500000\n")
                    script_condor.write('requirements = (OpSysAndVer =?= "CentOS7")\n')
                    script_condor.write("queue\n")
                    script_condor.close()
                    
                    # condor file submission                                                                                                                   
                    os.system("condor_submit %s/%s.condor" %(LOGDIR, s+'_'+str(i)))
                flist = ""
            i += 1


for s in SAMPLES:
    if len(s) <= 0 or s.startswith('#'): continue
    if len(options.filter) > 0 and not options.filter in s: continue
    print s
    if "2016" in options.year and not "Run2016" in s and not "Summer16" in s: continue
    if "2017" in options.year and not "Run2017" in s and not "Fall17" in s: continue
    if "2018" in options.year and not "Run2018" in s and not "Autumn18" in s: continue
    if not s in EV_v7 or not s in XS:
        print "- ERROR: sample", s, "has no events or cross section information, skipping..."
        continue
    print "+ Submitting", s
    runFileLSF(s)


if not options.test: print "+ Done."
else: print "+ Test ended, no job submitted."
