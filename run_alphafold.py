#!/usr/bin/env python3.8

import argparse
import datetime
import os
import subprocess
import sys
from os.path import abspath


def read_fasta(file_path):
    with open(file_path, 'r') as fp:
        name, seq = None, []
        for line in fp:
            line = line.rstrip()
            if line.startswith(">"):
                if name:
                    yield name, ''.join(seq)
                name, seq = line, []
            else:
                seq.append(line)
        if name:
            yield name, ''.join(seq)


def run(arguments):
    sequences = list(read_fasta(arguments.FASTA_file))
    num_chains = len(sequences)

    if num_chains == 0:
        raise ValueError('Your FASTA file does\'t appear to be valid. Please consult documentation here: '
                         'https://en.wikipedia.org/wiki/FASTA_format')
    for chain in sequences:
        if chain[1].upper() != chain[1]:
            raise ValueError('Your FASTA file does\'t appear to be valid. All residues must be specified '
                             f'using capital letters. Problem in sequence: {chain[1]}')
        if 'X' in chain[1]:
            raise ValueError('You have an unknown residue in your sequence - that isn\'t allowed. Problem in sequence '
                             f'{chain[1]}')

    total_aa = sum([len(_[1]) for _ in sequences])
    if total_aa > 800:
        print('AlphaFold uses memory in accordance with the total number of amino acids in all chains. '
              f'As you have more than 800 amino acids in total ({total_aa}), you may run out of memory when running '
              f'AlphaFold. You can look at the VM dashboard in your '
              'user profile and select a machine with high amounts of memory to try again, but ultimately very long '
              'sequences require more RAM than available on any NMRbox machine.')

    # Build the command
    command = ['singularity', 'exec', '--nv', '-B', arguments.database, '-B',
               arguments.output, '-B', arguments.FASTA_file, args.singularity_container]

    if num_chains == 1:
        print('Found FASTA file with one sequence, treating as a monomer.')
        command.append('/opt/alphafold/monomer.sh')
    elif num_chains > 1:
        print(f'Found FASTA file with {num_chains} sequences, treating as a multimer.')
        command.append('/opt/alphafold/multimer.sh')
    command.extend([arguments.database, arguments.FASTA_file, arguments.output, arguments.max_template_date])

    print(f'Running AlphaFold, this will take a long time.')
    try:
        subprocess.run(command, check=True, capture_output=True)
    except subprocess.CalledProcessError as err:
        print(f"AlphaFold raised an exception."
              f"{err.output.decode()}\n\nstderr:\n{err.stderr.decode()}")
        sys.exit(1)

    print(f"AlphaFold completed without exception. You can find your results in {abspath(arguments.output)}")


parser = argparse.ArgumentParser()
parser.add_argument("--database", "-d", action="store", default="/reboxitory/data/alphafold/1.0",
                    help='The path to the AlphaFold database to use for the calculation.')
parser.add_argument("--output-dir", "-o", action="store", default=".", dest='output',
                    help='The path where the output data should be stored. Defaults to the current directory.')
parser.add_argument("--max-template-date", "-t", action="store", default=str(datetime.date.today()),
                    dest='max_template_date',
                    help='If you are predicting the structure of a protein that is already in PDB'
                         ' and you wish to avoid using it as a template, then max-template-date must be set to'
                         ' be before the release date of the structure.')
parser.add_argument("--singularity-container", action="store",
                    default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'alphafold.sif'),
                    help=argparse.SUPPRESS)
parser.add_argument('FASTA_file', action="store",
                    help='The FASTA file to use for the calculation.')
args = parser.parse_args()

# Get absolute paths
args.database = abspath(args.database)
args.output = abspath(args.output)
args.FASTA_file = abspath(args.FASTA_file)
args.singularity_container = abspath(args.singularity_container)

# Ensure output directory is writeable
try:
    test_path = os.path.join(args.output, '.KD5cpxqYzBNqaBZ66guDuh33ns7JYz2jrKq')
    with open(test_path, 'w') as test:
        pass
    os.unlink(test_path)
except (IOError, PermissionError):
    raise IOError(f"Your specified output directory '{args.output}' is not writeable. Please choose a different output "
                  f"directory.")

run(args)
