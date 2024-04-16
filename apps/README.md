Applications compilation
============================


NAS and ccs-qcd 
---------------

We used the same version as the gem5 environment of this [repository](https://gitlab.com/domke/LARC).


QWS
---

We provide our makefile in apps/QWS.

We have chosen two problem sizes: small and large.

Small input:
```
./main 32 6 4 3   1 1 1 1    -1   -1  6 50
```

Large input:
```
./main 32 32 32 32   1 1 1 1    -1   -1  6 50
```

Genesis
-------

We used the Fugaku optimized 2.1.2 version.

To configure, run:
```
./configure --host=fugaku --enable-mixed
```

As we run the application with 4 MPI processes, we have adapted DHFR inputs from this [link](https://www.r-ccs.riken.jp/labs/cbrt/benchmark-2020/).

Copy apps/genesis/p4.inp to benchmark_mkl_ver4_nocrowding/npt/genesis2.0beta
/jac_amber/ from this [link](https://www.r-ccs.riken.jp/labs/cbrt/wp-content/uploads/2020/12/benchmark_mkl_ver4_nocrowding.tar.gz)

and run, from the benchmark_mkl_ver4_nocrowding/npt/genesis2.0beta
/jac_amber/ repository :
```
mpirun -n 4 spdyn p4.inp
```

with 3 OpenMP threads for source application and 8 for the target application.
