#!/bin/bash
#SBATCH -D /ufrc/lam/saravana8394/sst-elements-library-6.0.0/src/sst/elements/behavioralEmulation/tests
#SBATCH --job-name=1M-Big
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=saravana8394@ufl.edu
#SBATCH --account=ccmt
#SBATCH --qos=ccmt
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --mem=375gb
#SBATCH --distribution=cyclic:block
#SBATCH --partition=bigmem
#SBATCH -t 50:00:00
#SBATCH -o million_plus/data/1Million-64-saturday.txt
#SBATCH -e million_plus/err/1Million-64-saturday.err
 
module purge
ml add ufrc
ml add gcc/5.2.0 python boost/1.59.0 openmpi/1.10.2
export SST_CORE_HOME=/ufrc/lam/saravana8394/sstcore-6.0.0/mycore
export SST_ELEMENT_HOME=/ufrc/lam/saravana8394/sst-elements-library-6.0.0/sst_element_new
export PATH=${SST_ELEMENT_HOME}/bin:${SST_CORE_HOME}/bin:$PATH
 
./BE_RUN.sh -c titan-104876-bigmem.py -n 64 -v
