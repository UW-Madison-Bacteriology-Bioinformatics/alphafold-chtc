![Status - Testing](https://img.shields.io/badge/Status-Testing-2ea44f)


# Running AlphaFold on CHTC

AlphaFold is a protein structure database, and a tool that can predict 3D protein structure from sequence data. (https://alphafold.ebi.ac.uk/).
The Center for High Throughput Computing (https://chtc.cs.wisc.edu/) is a campus wide computing center at the University of Wisconsin-Madison that provides access to powerful computers to perform high throughput calculations for research. 

This repository aims to provide step-by-step instructions on how to set up AlphaFold on CHTC to predict protein structures. 

## Credits:
Build instructions from [non-docker setting](https://github.com/kalininalab/alphafold_non_docker) by kalininalab were used.
These instructions are also based off forked directories from @jsgro and @ChristinaLK:
- https://github.com/jsgro/alphafold_singularity
- https://github.com/ChristinaLK/alphafold_singularity

## Prerequisites
- A CHTC account (https://chtc.cs.wisc.edu/uw-research-computing/form.html)
- Prior experience with Bash and Unix
- Understanding of how files are organized on CHTC (e.g. `/home/`, `/staging/`, `/projects`) and how to submit a job using a container (`HTcondor`, `containers`)
  Resources:
  [Computing Guide](https://github.com/UW-Madison-Bacteriology-Bioinformatics/Computing/wiki) & 
  [How to use containers on CHTC, with examples](https://github.com/UW-Madison-Bacteriology-Bioinformatics/chtc-containers/blob/main/README.md)

> [!NOTE]
> If you want to get oriented, please feel free to schedule a 1-on-1 with the [Bioinformatics Research Support Service](https://bioinformatics.bact.wisc.edu/) by appointment, and/or meet a CHTC Facilitator during their office hours [CHTC Facilitators](https://chtc.cs.wisc.edu/uw-research-computing/get-help.html).

## Setup

Clone repository into your home directory and `cd` into the cloned folder. Then move into the `recipes` folder and use an interactive `build` job to create the SIF apptainer files.

```
cd alphafold-chtc
cd recipes
condor_submit -i build.sub
# Enter interactive build
apptainer build base-2.3.2.sif base-2.3.2.def
apptainer build alphafold-2.3.2.sif alphafold-2.3.2.def
# Test the containers:

# Move the container to an accessible location (e.g. projects or staging)
# replace the NETID or path as necessary.
mv *.sif /staging/YOURNETID/apptainer/.

# Leave the interactive build job
exit

pwd
# You should be in ~/alphafold-chtc/recipes
```

## Run AlphaFold Job

Customize or add the following options to a typical CHTC HTCondor submit file:

```
universe = container
container_image = alphafold.sif
requirements = (HasGpulabData == true)

transfer_executable = false
# replace with multimer.sh if applicable
executable = /opt/alphafold/monomer.sh
arguments = /gpulab_data/alphafold FASTA_file DIR 2020-04-08

transfer_input_files = alphafold.sif, FASTA_file

# request CPUs, GPUS, etc.
```


### Notes

* The alphafold.py run script has no requirements and should run in vanilla python 3.8.
* The run script allows customizing the database location and max_template_date. Call with `-h` to see usage information.
* By default, this uses the `monomer` model for monomers and the `multimer` model for multimers,
  and uses the `full_dbs` option for better quality results. For more details, see https://github.com/deepmind/alphafold#running-alphafold
  
Added note:

The `arguments` should contain 4 items:

- Databases dir: *e.g.* `/gpulab_data/alphafold`
- FASTA_file: fasta file containing sequence(s)
- DIR: directory to save into *e.g.* `${PWD}`
- 2020-04-08: cutoff date for PDB templates used.
