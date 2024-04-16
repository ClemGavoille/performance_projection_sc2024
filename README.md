Roofline projection workflow
============================

The workflow presented in this project can be splitted in 3 parts: analysis, data formatting and data processing.

Analysis can be done with any software as long as the results are correctly parsed in csv format for the data processing.

The first part of the workflow is the application and machine analysis.

For the application and cache analysis, our workflow relies on DynamoRIO (Version 10.0.x and higher).

Installing Dynamorio
----------------------------------------

See this [tutorial](https://dynamorio.org/page_building.html).

NOTE FOR A64FX ANALYSIS: 

On DynamoRIO 10.0 release, this small tweak is necessary for multi-threaded analysis on A64FX before running make install:

```
git apply patch dynamorio/patch/dynamorio.patch
```

The issue is tracked [here](https://github.com/DynamoRIO/dynamorio/issues/6451).

There is another patch (dynamorio/patch/dynamorio_genesis.patch) for disabling the processing of SVE scatter_gather instructions with drcachesim for genesis as there are instructions that are not yet implemented.
DynamoRIO needs to be compiled again after applying patch for processing genesis.


Installing client for Operational Intensity analysis
----------------------------------------

Run from dynamorio/clients

```
cmake -DDynamoRIO_DIR="<path>/<to>/<dynamorio>/<root>/cmake" clients/ ; make
```

Compiled libraries will be found in dynamorio/clients/bin/lib${client_name}.so. 

Make sure to use a recent compiler for compiling clients (aka not the default gcc 4.8.5) (use -DCMAKE_CXX_COMPILER and -DCMAKE_C_COMPILER flags).

We have two versions of our clients: normal and genesis.

genesis client disable processing of SVE scatter_gather instructions because of unsupported instructions by current version of DynamoRIO. It should be fixed in later releases. The impact of skipping these instructions is minimal when compared with cache numbers obtained with linux perf.


Running Operational Intensity analysis
----------------------------------------

## Command line :

```
drrun -c ./bin/libflops_bytes_noroi.so  -- <executable> <arguments>
```

Results are in the flops_bytes_PID.log file in you current directory in CSV format.

## Run with script

An example script to run client can be found in scripts/run_drrun.sh. 

OpenMP environment can be sourced within the script with the -o option.


Running Cache Analysis
--------------

We use [drcachesim](https://dynamorio.org/sec_drcachesim_tools.html#sec_tool_cache_sim) for cache behavior analysis. 

See the drcachesim documentation for further documentation on its usage.

## Run with script

An example script to run client can be found in scripts/run_drcachesim.sh. 

OpenMP environment can be sourced within the script with the -o option.


Source application performance measurement 
------------------------------------------

Measure the execution time in seconds of the application and fill the csv file by hand. See the empty headers in headers/empty_run_results.csv.

Machine Description
-------------------

This was also done by hand as the input for [High Performance Linpack](https://www.netlib.org/benchmark/hpl/) and [Stream](https://www.cs.virginia.edu/stream/) benchmarking is machine-dependent. 

We also used the Stream benchmark with vectors size equal to the cache size to measure cache levels bandwidth.

Machine description csv headers can be found in the headers/empty_machine.csv

This is where we can extrapolate stream and HPL values to represent an hypothetical machine.


Data processing 
---------------

scripts/roofline_projection.py needs data of OI analysis, cache simulation, runtime measurement, and machine description to be in the correct CSV format as input files .

The data used in paper can be found in experiments/ as all_OI_analysis.csv, all_cache_analysis.csv, and run.csv as an example. Machine description file can be found in machines/

We also give a script to process drcachesim output in scripts/dynamorio_output_processing.sh.


Performance projection
----------------------------

Once data are formatted, run 
```
scripts/roofline_projection.py <OI_file> <runtime_file> <cache_file> <machine_file> --sa <source_application_id> --ta <target_application_id> --sm <source_machine_id> --tm <target_machine_id>
```

See ./scripts/roofline_projection.py --help for further documentation.

## Reproducing paper results

All the data needed to reproduce the results presented in the article are contained in the experiments/ folder.

As an example, to make projection between IS-OMP from A64FX to LARC_C, run:

```
scripts/roofline_projection.py experiments/all_OI_analysis.csv experiments/run.csv experiments/all_cache_analysis machines/A64FX.csv --sa is.B.x_A64FX --ta is.B.x_LARC_C --sm CMG_A64FX --tm CMG_LARC_C
```

## Plotting paper figures

The scripts/plot_bar.py is used to plot these figures from the experiments/results_projection.csv

```
./scripts/plot_bar.py experiments/results_projection.csv
```

Contact
----------

Feel free to ask any question at: clement.gavoille@protonmail.com
