#!/bin/bash
#SBATCH -D /ufrc/lam/saravana8394/sst-elements-library-6.0.0/src/sst/elements/behavioralEmulation/tests
#SBATCH --job-name=1MB8
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=saravana8394@ufl.edu
#SBATCH --account=ccmt
#SBATCH --qos=ccmt
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --mem=295gb
#SBATCH --distribution=cyclic:block
#SBATCH --partition=bigmem
#SBATCH -t 40:00:00
#SBATCH -o million_plus/data/1Million-bigmem-trySunday-8Ranks.txt
#SBATCH -e million_plus/err/1Million-bigmem-trySunday-8Ranks.err
 
module purge
ml add ufrc
ml add gcc/5.2.0 python boost/1.59.0 openmpi/1.10.2
export SST_CORE_HOME=/ufrc/lam/saravana8394/sstcore-6.0.0/mycore
export SST_ELEMENT_HOME=/ufrc/lam/saravana8394/sst-elements-library-6.0.0/sst_element_new
export PATH=${SST_ELEMENT_HOME}/bin:${SST_CORE_HOME}/bin:$PATH
 
./BE_RUN.sh -c titan-104876-bigmem-8.py -n 8 -v
