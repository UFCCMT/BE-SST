#!/bin/bash
#SBATCH -D /ufrc/lam/saravana8394/sst-elements-library-6.0.0/src/sst/elements/behavioralEmulation/tests
#SBATCH --job-name=16K
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=saravana8394@ufl.edu
#SBATCH --account=ccmt
#SBATCH --qos=ccmt
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --nodes=2
#SBATCH --exclusive
#SBATCH --distribution=cyclic:block
#SBATCH --mem-per-cpu=2GB
#SBATCH --partition=hpg1-compute
#SBATCH -t 03:00:00
#SBATCH -o symbolic_results/16K.txt
#SBATCH -e symbolic_results/16K.err

ml add ufrc
ml add gcc/5.2.0 python boost/1.59.0 openmpi/1.10.2
export SST_CORE_HOME=/ufrc/lam/saravana8394/sstcore-6.0.0/mycore
export PATH=${SST_CORE_HOME}/bin:$PATH
export SST_ELEMENT_HOME=/ufrc/lam/saravana8394/sst-elements-library-6.0.0/sst_element_core_new
export PATH=${SST_ELEMENTS_HOME}/bin:$PATH
#mpirun -n 8 ./BE_RUN.sh -c vulcan-proper.py -v
./BE_RUN.sh -c vulcan-proper-symbolic-16K.py -n 32 -N 100 -v

