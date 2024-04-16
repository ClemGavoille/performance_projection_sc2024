## Installing Dynamorio

See this [tutorial](https://dynamorio.org/page_building.html).

NOTE FOR A64FX ANALYSIS: 

On DynamoRIO 10.0 release, this small tweak is necessary for multi-threaded analysis on A64FX:

```
diff --git a/core/unix/signal.c b/core/unix/signal.c
index 907678000..713cff58d 100644
--- a/core/unix/signal.c
+++ b/core/unix/signal.c
@@ -934,7 +934,7 @@ get_clone_record(reg_t xsp)
      * before get_clone_record() is called.
      */
 #ifdef AARCH64
-    dstack_base = (byte *)ALIGN_FORWARD(xsp, PAGE_SIZE) + PAGE_SIZE;
+    dstack_base = (byte *)ALIGN_FORWARD(xsp, PAGE_SIZE);
 #else
     dstack_base = (byte *)ALIGN_FORWARD(xsp, PAGE_SIZE);
 #endif
```

The issue is tracked [here](https://github.com/DynamoRIO/dynamorio/issues/6451).

## Installing clients 

Run cmake -DDynamoRIO_DIR="<path>/<to>/<dynamorio>/<root>/cmake" clients/ ; make

Compiled libraries will be found in ./bin/lib${client_name}.so. 

Make sure to use a recent compiler for compiling clients (aka not the default gcc 4.8.5) (use -DCMAKE_CXX_COMPILER and -DCMAKE_C_COMPILER flags)

## Run 

For OI analysis :

drrun -c ./bin/libflops_bytes_noroi.so  -- <executable> <arguments>

Results are in the flops_bytes_PID.log file in you current directory in csv format.

## Run with script

You can run an OI analysis with the ./run_scripts/run_drrun.sh command. 

OpenMP environment can be sourced within the script with the -o option.

