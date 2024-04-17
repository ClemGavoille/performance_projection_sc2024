#!/bin/bash

OMP_DEFAULT=1
TRACE_SIZE=6000 # Maximum trace size in MB per thread

DYNAMORIO_DIR= #Add the root of your own dynamorio directory
TRACE_DIR=$(pwd) # Directory for the processed trace files, default is current directory
TMP_TRACE_DIR=$(pwd) # Directory for the raw trace files, default is current directory
while [[ $# -gt 0 ]]; do
	case $1 in
		-c|--caches)
			cache_conf="$2"
			shift # past argument
			shift # past value
			;;
		-o|--omp)
			source $2
			OMP_DEFAULT=0
			shift # past argument
			shift # past value
			;;
		-h|--help)
			echo "Usage : ./run_drcachesim.sh -c <caches_config_files> -o <OpenMP environment variables> <binary> <args>"
			exit 1
			;;
		-*|--*)
			echo "Unknown option $1"
			exit 1
			;;
		*)
			POSITIONAL_ARGS+=("$1") # save positional arg
			shift # past argument
			;;
	esac
done

set -- "${POSITIONAL_ARGS[@]}"
if [[ -n $1 ]]; then


	if [[ "$OMP_DEFAULT" -eq 1 ]]; then  # Default OpenMP environment
		export OMP_NUM_THREADS=12
		export OMP_PROC_BIND=close
		export OMP_PLACES=cores
	fi

	appname=$(basename $1)

	echo "Running drcachesim"
	mkdir -p  $TMP_TRACE_DIR/$appname
	$DYNAMORIO_DIR/bin64/drrun -t drcachesim -raw_compress gzip -coherence -offline -L0I_filter -L0I_size 0 -max_trace_size ${TRACE_SIZE}M -outdir $TMP_TRACE_DIR/$appname/ -- $@ 
	mkdir -p $TRACE_DIR/$appname
	echo "Trace pre-processing"
	$DYNAMORIO_DIR/clients/bin64/drraw2trace -compress gzip -jobs 16 -indir $TMP_TRACE_DIR/$appname/drmemtrace.*.dir -out $TRACE_DIR/$appname 

	for i in $cache_conf
	do
		echo "Trace processing, cache configuration: $i"
		$DYNAMORIO_DIR/bin64/drrun -t drcachesim -jobs 16 -compress gzip -config_file $i -coherence -indir $TRACE_DIR/$appname 2> ${appname}_$(basename ${i})_cache_results
	done

	rm -rf $TRACE_DIR/$appname
else
	echo "ERROR: no binary"
	exit 1
fi

