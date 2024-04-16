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

Run 

```
cmake -DDynamoRIO_DIR="<path>/<to>/<dynamorio>/<root>/cmake" clients/ ; make
```

Compiled libraries will be found in ./bin/lib${client_name}.so. 

Make sure to use a recent compiler for compiling clients (aka not the default gcc 4.8.5) (use -DCMAKE_CXX_COMPILER and -DCMAKE_C_COMPILER flags).

We have two versions of our clients: normal and genesis.

genesis client disable processing of SVE scatter_gather instructions because of unsupported instructions by current version of DynamoRIO. It should be fixed in later releases.


Running Operational Intensity analysis
----------------------------------------

## Command line :

```
drrun -c ./bin/libflops_bytes_noroi.so  -- <executable> <arguments>
```

Results are in the flops_bytes_PID.log file in you current directory in csv format.

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

You can run scripts/roofline_projection.py with input csv files obtained with armie, cache and time analysis and machine description.

See ./scripts/roofline_projection.py --help for further documentation.

Article results reproduction
----------------------------

All the data needed to reproduce the results presented in the article are contained in the results/ folder.

Results needed for validation are in the results/validation folder.

Command line to generate a graph similar to the validation (without the target performance) results :

```

./scripts/roofline_projection.py ./results/validation/*.csv ./results/validation/machines/*.csv --sa ep_n1,mg_n1,cg_n1,ft_n1,bt_n1,sp_n1,lu_n1,lul_n1,lmp_n1 --sm aws_neoverse_n1_64core --ta ep_v1,mg_v1,cg_v1,ft_v1,bt_v1,sp_v1,lu_v1,lul_v1,lmp_v1 --tm aws_neoverse_v1_64core --plot_bar


./scripts/roofline_projection.py ./results/validation/*.csv ./results/validation/machines/*.csv --ta ep_n1,mg_n1,cg_n1,ft_n1,bt_n1,sp_n1,lu_n1,lul_n1,lmp_n1 --tm aws_neoverse_n1_64core --sa ep_v1,mg_v1,cg_v1,ft_v1,bt_v1,sp_v1,lu_v1,lul_v1,lmp_v1 --sm aws_neoverse_v1_64core --plot_bar

```

Results needed for projection toward an epi-like machine on LULESH are in the results/epi_projection/ folder.

Command line to generate a graph similar to the projection on epi-like results:

```

./scripts/roofline_projection.py results/epi_projection/*.csv results/epi_projection/machines/neoverse_v1.csv --sa lul_gcc_v1,lul_gcc_v1_sve,lul_armclang_v1,lul_armclang_v1_sve --sm aws_neoverse_v1_64core --ta lul_gcc_v1_big,lul_gcc_v1_big_sve,lul_armclang_v1_big,lul_armclang_v1_big_sve --tm epi_like --plot_bar

```

Folders
-------

* clients -> Contains the sample folder to copy in armie source
* include -> Contains the markers headers for source code RoI analysis
* headers -> Contains the empty headers of csv file needed for roofline projection
* scripts -> Contains scripts needed for data processing
* results -> Contains all the data needed to reproduce the results presented in the article in validation/ and epi_projection/ folders
* reproduction -> Contains the source code of the small kernels used to reproduce the OI behavior on KNL

Contact
----------

Feel free to ask any question at: clement.gavoille@protonmail.com
