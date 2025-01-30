#!/bin/bash

DB_PATH="$1"
FASTA="$2"
DATE="$3"

# run multimer or monomer
bash ./multimer.sh ${DB_PATH} ${FASTA} $(pwd) ${DATE} -m multimer

# save results and compress
tar cvf `basename ${FASTA} .fa`.tar `basename ${FASTA} .fa`
gzip `basename ${FASTA} .fa`.tar 

# Print the file names, for troubleshooting:
ls -lh `basename ${FASTA} .fa`.tar.*

# Use transfer_output_files to export and remap to your staging folder
