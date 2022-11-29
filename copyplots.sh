#!/bin/sh
#
#SBATCH --account=apam
#SBATCH --job-name=scopy
# SBATCH --gres=gpu:1             # Request 1 gpu (Up to 4 on K80s, or up to 2 on P100s are valid).
#SBATCH -c 1                     # The number of cpu cores to use.
#SBATCH --time 02:00:00              # The time the job will take to run.
#SBATCH --mem-per-cpu=1gb        # The memory the job will use per cpu core.
#SBATCH --mail-type=ALL

#module load anaconda/3-5.1
#module load anaconda
#mkdir results3

#cd storm-surge
mkdir storm-surge/keep_plots_t4
for d in $(<timeouts.txt);do
#    mkdir "storm-surge/keep_plots_t4/"$d"_output"
#    cp -r "storm-surge/holland80-amr2/"$d"_plots" storm-surge/keep_plots_t4/.
    cd "storm-surge/holland80-amr2/"$d"_output/"
    mkdir keep_output
    cp gauge0* keep_output/.
    cd ../../..
    mv "storm-surge/holland80-amr2/"$d"_output/keep_output" "storm-surge/keep_plots_t4/"$d"_output" 
done
cd storm-surge
tar -czvf keep_plots_t4.tar.gz keep_plots_t4

