#!/bin/bash

OMP_DEFAULT=1
DYNAMORIO_DIR= #Add the root of your own dynamorio directory
CLIENTS_DIR= #Add the folder containing compiled clients

while [[ $# -gt 0 ]]; do
	case $1 in
		-o|--omp)
			source $2
			OMP_DEFAULT=0
			shift # past argument
			shift # past value
			;;
		-h|--help)
			echo "Usage : ./run_drrun.sh -o <OpenMP environment variables> <binary> <args>"
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

	app_name=$(basename $1)

	${DYNAMORIO_DIR}/bin64/drrun -c ${CLIENTS_DIR}/libflops_bytes_noroi.so -- $@ ; 
else
	echo "ERROR: no binary"
	exit 1
fi
