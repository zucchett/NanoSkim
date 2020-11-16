# H -> J/Psi Gamma analysis setup

### Preliminary operations and plotting:

Create symbolic links to some configuration files in the `Analysis/` directory:

`source makeLinks.sh`

To make a plot:

 - select or define a variable from the `variables.py` file
 
 - select or define a category/selection in the file `aliases.py`
 
 - check in `plot.py` that the ntuple location, the signal and background definition, and the blind flag are correctly set (warning: the background list cannot be empty)
 
Run the macro with the command: `plot.py -v <variable_name> -c <category_name>` (without `<>`)

Add the option `-n` to show the MC distributions normalized to data.


### Fitting

Create a subset of ntuples with just the events needed to run the fit with `python pico.py -p`. Remember to check first the input and output directories, or specify them with the `-i` and `-o` arguments, respectively.


The fitting macro can be run category-by-category by hand, or all categories in a row with `python dijet.py -a -b`. The option `-a` runs all the categories, and `-b` forces the batch mode.

The fitting macro produces:

 - fitting plots in the `fits/<category_name>/` directory
 
 - the workspaces in the `workspaces/` directory. They contain the datasets and the parametric functions (background and signals) to be used in the final fit.
 
 - the datacards in the `datacards/` directory. They contain the datacards, text files that specify all the informations to be provided to `combine` for the fit.
 

### Prepare and run the combined fit

Datacards are not automatically merged; the macro that does that is run with `source combineCards.sh`, and produces another datacard that combines the information from the input cards.

The fits are performed with `combine`, which has the be installed in the same CMSSW release. Among the many options, the most interesting commonds are:

 - `combine -M AsymptoticLimits <path_to_the_datacard>` to run the limits with the Asymptotic approximation
 
 - `combine -M Significance -t -1 --expectSignal=1  <path_to_the_datacard>` to get the expected significance in number of standard deviations
  
All these commands are conveniently included in `run.sh`.
