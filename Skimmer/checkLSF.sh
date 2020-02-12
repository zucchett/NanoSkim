#!/bin/bash

njobs=$(ls LSF/outfile* | wc -l)
ndone=$(cat LSF/outfile* | grep "+ Done." | wc -l)
echo Number of successful jobs: $ndone/$njobs
