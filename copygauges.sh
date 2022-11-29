#!/bin/sh
#
#SBATCH --account=apam
#SBATCH --job-name=scopy
# SBATCH --gres=gpu:1             # Request 1 gpu (Up to 4 on K80s, or up to 2 on P100s are valid).
#SBATCH -c 1                     # The number of cpu cores to use.
#SBATCH --time 01:00:00              # The time the job will take to run.
#SBATCH --mem-per-cpu=1gb        # The memory the job will use per cpu core.
#SBATCH --mail-type=ALL

#module load anaconda/3-5.1
#module load anaconda
#mkdir results3

#cd storm-surge
#mkdir timeout_output
for d in $(<timeouts.txt);do
    mkdir "storm-surge/timeout_output/"$d"_output"
    cp "storm-surge/holland80-amr2/"$d"_output/gauge00013.txt" "storm-surge/timeout_output/"$d"_output/gauge00013.txt"
#    cp "holland80-amr2/"$d"_output/gauge00001.txt" "f4000/"$d"_output/gauge00001.txt"
done

