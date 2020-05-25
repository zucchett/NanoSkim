# NanoSkim setup

1. On a t2-ui-* or equivalent machine, install a recent CMSSW release (`CMSSW_10_2_6`, for instance) if its not already available:

`cmsrel CMSSW_10_2_6`

`cd CMSSW_10_2_6/src/`

`cmsenv`

2. Clone the repository in the `src` directory:

 - with SSH: `git clone git@github.com:zucchett/NanoSkim.git`
 
 - with HTTPS: `git clone https://github.com/zucchett/NanoSkim.git`

3. Compile with `scram b`.

Check the individial packages for futher instructions.
