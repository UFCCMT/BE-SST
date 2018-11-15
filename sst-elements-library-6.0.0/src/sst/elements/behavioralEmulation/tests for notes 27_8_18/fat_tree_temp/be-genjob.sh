#!/bin/bash

if [ $# -lt 2 ]; then
        echo "x---x---x---x---x---x---x---x---x"
        echo "No command line argument supplied"
        echo "Run again with jobscript folder and data folder name  as cmd line inputs"
	      echo "Usage: ./be-genjob.sh <job_folder> <data_folder>"
        echo "x---x---x---x---x---x---x---x---x"
        exit 0
fi

#bone-be parameters
TIMESTEP=1
E_SIZE="5 6 9 11 16 17" 
EPP="4,4,4"
#NP="16 256 2048 16384 131072 262144 524288 1048576 2097152" 
NP="262144 524288" 
PHY_PARAM=5

#Test case!!
#E_SIZE=5
#EPP=8 #"8 24 70 125 180"
#CART="8 32 200 1352 8192"
#CART_X=32
#CART_Y=16
#CART_Z=16

#Machine Parameters
Tlnum_proc=32
one=1

#Creating array stack for EPP
epp_stack=$(echo $EPP | tr ";" "\n")

#Check for job dir to store job scripts
if [ ! -d "$1" ]; then
    mkdir $1/
fi

#Check for data dir to store *.out and *.err
if [ ! -d "$2" ]; then
    mkdir $2/
    mkdir $2/err
fi

echo "Creating job file(s)..."

for ELE_SIZE in $E_SIZE
do
  for Exyz in $epp_stack
  do
    #Calculating EL_X, EL_Y,EL_Z from epp_stack
    EL_X=$(echo $Exyz | tr "," " " | awk '{print $1}')
    EL_Y=$(echo $Exyz | tr "," " " | awk '{print $2}')
    EL_Z=$(echo $Exyz | tr "," " " | awk '{print $3}')
    EC=$((EL_X*EL_Y*EL_Z))
    for NUM_TASKS in $NP
    do
      #Time and memory assignment
      if [ $NUM_TASKS -eq 131072 ];
        then
        MEM="1500mb"
        TASKS=64
        if [ $EC -le 100 ]; then
          wtime="23:30:00"
        elif [ $EC -ge 128 ]; then
          wtime="23:50:00"
        else
          wtime="24:00:00"
        fi
      elif [ $NUM_TASKS -eq 16384 ];
        then
        MEM=""
        TASKS=32
        if [ $EC -le 100 ]; then
          wtime="05:00:00"
        elif [ $EC -ge 128 ]; then
          wtime="01:55:00"
        else
          wtime="02:15:00"
        fi
      elif [ $NUM_TASKS -eq 2048 ]; 
        then
        MEM="600mb"
        TASKS=8
        if [ $EC -le 100 ]; then
          wtime="02:12:00"
        elif [ $EC -ge 128 ]; then
          wtime="00:35:00"
        else
          wtime="00:50:00"
        fi
      elif [ $NUM_TASKS -eq 256 ]; 
        then
        MEM="2gb"
        TASKS=1
        if [ $EC -le 100 ]; then
          wtime="00:50:00"
        elif [ $EC -eq 128 ]; then
          wtime="00:20:00"
        elif [ $EC -eq 256 ]; then
          wtime="00:30:00"
        else
          wtime="00:40:00"
        fi
      elif [ $NUM_TASKS -eq 16 ]; 
        then
        MEM="256mb"
        TASKS=1
        if [ $EC -le 100 ]; then
          wtime="00:30:00"
        elif [ $EC -ge 128 ]; then
          wtime="00:15:00"
        else
          wtime="00:30:00"
        fi
      elif [ $NUM_TASKS -eq 262144 ];
        then
        MEM="2gb"
        TASKS=64
        if [ $EC -le 100 ]; then
          wtime="02:40:00"
        elif [ $EC -ge 128 ]; then
          wtime="03:05:00"
        else
          wtime="03:30:00"
        fi
      elif [ $NUM_TASKS -eq 524288 ];
        then
        MEM="2gb"
        TASKS=64
        if [ $EC -le 100 ]; then
          wtime="03:40:00"
        elif [ $EC -ge 128 ]; then
          wtime="04:05:00"
        else
          wtime="04:30:00"
        fi
      elif [ $NUM_TASKS -eq 1048576 ];
        then
        MEM="3gb"
        TASKS=128
        if [ $EC -le 100 ]; then
          wtime="05:20:00"
        elif [ $EC -ge 128 ]; then
          wtime="05:45:00"
        else
          wtime="06:00:00"
        fi
      else
    	MEM="3gb"
    	TASKS=128
    	wtime="9:00:00"
      fi

      NUM_NODES1=$((TASKS/Tlnum_proc))
      NUM_NODESr=$((TASKS%Tlnum_proc))
      if [ $NUM_NODESr -eq 0 ];
      then
          NUM_NODES=$NUM_NODES1
      else
          NUM_NODES=$((NUM_NODES1+one))
      fi

#  	  if [ $EL_X = $EL_Y ] && [ $EL_Y = $EL_Z ]; 
#  	  then
      	  #Making the job script
      	  echo '#!/bin/bash' > jobfile
      	  echo '#SBATCH -D '`pwd` >> jobfile
      	  echo '#SBATCH --job-name=be_sim-es'$ELE_SIZE'ec'$EC'np'$NUM_TASKS'.job' >>jobfile	#Job name
      	  echo '#SBATCH --mail-type=FAIL' >> jobfile		#Mail events (NONE,BEGIN,END,FAIL,ALL)
      	  echo '#SBATCH --mail-user=saravana8394@ufl.edu'  >>jobfile		#your email id
          echo '#SBATCH --account=ccmt' >> jobfile    #Account name
          echo '#SBATCH --qos=ccmt' >> jobfile    #qos 
      	  echo "#SBATCH --ntasks=$TASKS" >> jobfile		#Number of MPI ranks
      	  echo "#SBATCH --cpus-per-task=1" >> jobfile			#Number of cores per MPI rank
      	  echo "#SBATCH --nodes=$NUM_NODES" >> jobfile		#Number of Nodes
      	  echo "#SBATCH --mem-per-cpu=$MEM" >> jobfile			#Per processor memory
          echo '#SBATCH --ntasks-per-socket=16' >> jobfile  #task per socket
          echo '#SBATCH --exclusive'  >> jobfile    #node exclusivity
          echo '#SBATCH --distribution=cyclic:block' >> jobfile   #cyclic distibution by schedular
	  echo '#SBATCH --partition=hpg2-compute' >> jobfile      #Partition in which it should run
      	  echo "#SBATCH -t $wtime" >> jobfile				#Walltime
      	  echo '#SBATCH -o '$2'/bonebe-es'$ELE_SIZE'ec'$EC'np'$NUM_TASKS'.csv' >> jobfile	#STDOUT
      	  echo '#SBATCH -e '$2'/err/be_sim-es'$ELE_SIZE'ec'$EC'np'$NUM_TASKS'.err' >> jobfile	#STDERR
      	  echo " " >> jobfile
      	  echo "module purge" >> jobfile
          echo "ml add ufrc" >> jobfile
      	  echo "ml add gcc/5.2.0 python boost/1.59.0 openmpi/1.10.2" >> jobfile
	  echo "export SST_CORE_HOME=/ufrc/lam/saravana8394/sstcore-6.0.0/mycore" >> jobfile
	  echo "export SST_ELEMENT_HOME=/ufrc/lam/saravana8394/sst-elements-library-6.0.0/sst_element_new" >> jobfile
	  echo 'export PATH=${SST_ELEMENT_HOME}/bin:${SST_CORE_HOME}/bin:$PATH' >> jobfile
      	  echo " " >> jobfile
      	  echo './BE_RUN.sh -c titan-proper-es'$ELE_SIZE'ec'$EC'np'$NUM_TASKS'.py -n '$TASKS >> jobfile
      	  mv jobfile be_sim'-es'$ELE_SIZE'ec'$EC'np'$NUM_TASKS'.job'
          mv be_sim'-es'$ELE_SIZE'ec'$EC'np'$NUM_TASKS'.job' $1
#  	  fi
    done
  done
done

echo "Job file(s) created!"
echo " "
echo "Listing Jobfile(s):"
echo "---------------------------------------------------------------"
ls $1
echo "----------------------------------------------------------------"
sleep 2
echo " "
echo "Job file(s) present in $1/ folder"
echo "Output and error files present in $2/ folder"
echo " "

#Submit jobscript
echo "Submitting Job files:-"

for ELE_SIZE in $E_SIZE
do
 for Exyz in $epp_stack
 do
  EL_X=$(echo $Exyz | tr "," " " | awk '{print $1}')
  EL_Y=$(echo $Exyz | tr "," " " | awk '{print $2}')
  EL_Z=$(echo $Exyz | tr "," " " | awk '{print $3}')
  EC=$((EL_X*EL_Y*EL_Z))
  for NUM_TASKS in $NP
  do
#   if [ $EL_X = $EL_Y ] && [ $EL_Y = $EL_Z ];
#   then
      sbatch $1/be_sim'-es'$ELE_SIZE'ec'$EC'np'$NUM_TASKS'.job'
#   fi
  done
 done
done

echo "* * * * -----------Completed!----------- * * * *"
