# NanoSkim setup


### Prerequisites:


#### As part of a CMSSW release (recommended):
 
On a t2-ui-* or equivalent machine, install a recent CMSSW release (`CMSSW_10_2_13`, for instance):

`cmsrel CMSSW_10_2_13`

`cd CMSSW_10_2_13/src/`

`cmsenv`

Then, install the *nanoAOD-tools* package. Follow the instructions on the github page `https://github.com/cms-nanoAOD/nanoAOD-tools`, section "Checkout instructions: CMSSW".


#### Standalone (untested):

Install the *nanoAOD-tools* package. Follow the instructions on the github page `https://github.com/cms-nanoAOD/nanoAOD-tools`, section "Checkout instructions: standalone". Python 2.7 and ROOT have to be installed first.


### Installation of the package

Clone the repository in the `src` directory:

`cd $CMSSW_BASE/src`

 - with SSH: `git clone git@github.com:zucchett/NanoSkim.git`
 
 - with HTTPS: `git clone https://github.com/zucchett/NanoSkim.git`

if in a CMSSW environment, compile with `scram b`.

Check the individial packages for futher instructions.
