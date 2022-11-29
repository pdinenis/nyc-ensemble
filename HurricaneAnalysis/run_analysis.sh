#!/bin/sh
#
#SBATCH --account=apam
#SBATCH --job-name=sanalyse
#SBATCH -c 1                     # The number of cpu cores to use.
#SBATCH --time 00:30:00              # The time the job will take to run.
#SBATCH --mem-per-cpu=1gb        # The memory the job will use per cpu core.
#SBATCH --mail-type=ALL

module load anaconda/3-5.1
python HA.py
