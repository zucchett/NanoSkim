# Plotting instructions

There are two ways to produce plots from extended NanoAOD.

Before plotting, few configuration files have to be up-to-date with the latest definitions:

- `samples.py` defines the list of samples, merged in groups for plotting
- `aliases.py` defines the names of the categories and the corresponding selections
- `variables.py` the variables used for plotting, including the ranges, the scales, and axis titles
   
## Projecting from Tree

This method uses the TTree:Project method invoked by the `plot.py` macro. It's sufficient to specify the variable (that has to be defined in =variables.py=) with the `-v` option, and the short category name (defined in =aliases.py=) with the `-c` option. For example:
```
python plot.py -v Z_mass -c Z2mCR
```
Without other options, project jobs are parallelized for each subsample.


## Loop on events

It's also possible to perform a loop on events to perform more complex selections and calculate new variables on-the-fly. In this case, two separate macros are used:
- `run.py` handles the parallelization, the definition of the histograms, and saving the output
- `loop.py` hosts the code that runs over each events. It consist on an initial part where the rootfile is opened, the Tree imported, and the loop is started. The arguments passed to the `loop()` function are a dictionary of a dictionary of TH1F, where the first key has to be the name of the category (defined in the header of the file), and the second has to be the name of the variable (also defined in the header).
To run the loop macro, simply type:
```
python run.py
```
The jobs can be parallelized to speed-up time. The single core mode should be used before parallelizing because it's much easier to debug the code (by parallelizing, error messages are suppressed).
The number of jobs is defined as the number of virtual cores of the machine - 4 to have free spare cores. In case of the t2-ui there are 32 -4 = 28 cores available.
The parallel mode is enabled by adding the option `-p`:
```
python run.py -p
```
The name of the output file can be specified with the option `-o`:
```
python run.py -p -o output.root
```
The roofile contains the histograms written in hyerarchical directories, according to the `category/variable/sample` structure.

The histograms can be plotted with the macro `plot.py`, with the same syntax explained before, but adding the specification of the output rootfile. For example:
```
python plot.py -v Z_mass -c Z2mCR -f output.root
```

