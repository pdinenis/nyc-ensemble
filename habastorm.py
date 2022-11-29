r"""Batch sub-classes for geoclaw storm runs on the Columbia Habanero machine"""

# ============================================================================
#      Copyright (C) 2017 Kyle Mandli <kyle.mandli@columbia.edu>
#
#          Distributed under the terms of the MIT license
#                http://www.opensource.org/licenses/
# ============================================================================

from __future__ import print_function
from __future__ import absolute_import

import os
import glob
import subprocess

import time 
import pdb  

import batch


class HabaneroStormJob(batch.Job):
    r"""
    Modifications to the basic :class:`batch.Job` class for Habanero runs

    """

    def __init__(self):
        r"""
        Initialize Habanero job

        See :class:`HabaneroStormJob` for full documentation
        """

        super(HabaneroStormJob, self).__init__()

        # Add extra job parameters
        self.omp_num_threads = 24
        self.mic_omp_num_threads = 1
        self.mic_affinity = "none"
        self.time = "12:00:00"
        # TODO:  check to see what the queue should be
        self.queue = "serial"


class HabaneroStormBatchController(batch.BatchController):
    r"""
    Modifications to the basic batch controller for Habanero runs


    :Ignored Attributes:

    Due to the system setup, the following controller attributes are ignored:

        *plot*, *terminal_output*, *wait*, *poll_interval*, *plotclaw_cmd*
    """

    def __init__(self, jobs=[]):
        r"""
        Initialize Habanero batch controller

        See :class:`HabaneroStormBatchController` for full documentation
        """

        super(HabaneroStormBatchController, self).__init__(jobs)

        # Habanero specific execution controls
        self.email = None

    def run(self):
        r"""Run Habanero jobs from controller's *jobs* list.

        This run function is modified to run jobs through the slurm queue 
        system and provides controls for running serial jobs (OpenMP only).

        Unless otherwise noted, the behavior of this function is identical to
        the base class :class:`BatchController`'s function.
        """

        # Run jobs
        paths = []
        for (i, job) in enumerate(self.jobs):
            # Create output directory
            data_dirname = ''.join((job.prefix, '_data'))
            output_dirname = ''.join((job.prefix, "_output"))
            plots_dirname = ''.join((job.prefix, "_plots"))
            run_script_name = ''.join((job.prefix, "_run.sh"))
            log_name = ''.join((job.prefix, "_log.txt"))

            if len(job.type) > 0:
                job_path = os.path.join(self.base_path, job.type, job.name)
            else:
                job_path = os.path.join(self.base_path, job.name)
            job_path = os.path.abspath(job_path)
            data_path = os.path.join(job_path, data_dirname)
            output_path = os.path.join(job_path, output_dirname)
            plots_path = os.path.join(job_path, plots_dirname)
            log_path = os.path.join(job_path, log_name)
            run_script_path = os.path.join(job_path, run_script_name)
            paths.append({'job': job_path, 'data': data_path,
                          'output': output_path, 'plots': plots_path,
                          'log': log_path})

            # Create job directory if not present
            if not os.path.exists(job_path):
                os.makedirs(job_path)

            # Clobber old data directory
            if os.path.exists(data_path):
                if not job.rundata.clawdata.restart:
                    data_files = glob.glob(os.path.join(data_path, '*.data'))
                    for data_file in data_files:
                        os.remove(data_file)
            else:
                os.mkdir(data_path)

            # Write out data
            temp_path = os.getcwd()
            os.chdir(data_path)
            job.write_data_objects()
            os.chdir(temp_path)

            # Handle restart requests
            if job.rundata.clawdata.restart:
                restart = "T"
                overwrite = "F"
            else:
                restart = "F"
                overwrite = "T"

            # Construct string commands
            run_cmd = "%s %s %s %s %s %s True\n" % (self.runclaw_cmd,
                                                    job.executable,
                                                    output_path,
                                                    overwrite,
                                                    restart,
                                                    data_path)

            plot_cmd = "%s %s %s %s \n" % (self.plotclaw_cmd,
                                            output_path,
                                            plots_path, 
                                            job.setplot) 

            gauge_max_program = os.path.join(self.base_path, "process-scripts", "get_gauge_max.py")  
            gauge_cmd = "python %s %s %s %s %s \n" %(gauge_max_program, output_path, self.base_path, job.name, job.prefix)  
            
            #remove_cmd = "rm -rf %s %s %s %s\n" %(output_path, plots_path, log_path, run_script_path)   
            remove_cmd = "rm -rf %s %s %s %s\n" %(output_path, plots_path, data_path, run_script_path)   

            # Write slurm run script
            run_script = open(run_script_path, 'w')

            run_script.write("#!/bin/sh\n")
            run_script.write("#SBATCH --account apam         # Job account\n")
            run_script.write("#SBATCH -J %s                  # Job name\n" % job.prefix)
            run_script.write("#SBATCH -o %s                  # Job log \n" % log_path)
            run_script.write("#SBATCH -n 1                   # Total number of MPI tasks requested\n")
            run_script.write("#SBATCH -N 1                   # Total number of MPI tasks requested\n")
            run_script.write("#SBATCH -p %s                  # queue\n" % job.queue)
            run_script.write("#SBATCH -t 10:30:00             # run time (hh:mm:ss)\n")
            if self.email is not None:
                run_script.write("#SBATCH --mail-user=%s \n" % self.email )
                #run_script.write("#SBATCH --mail-type=begin       # email me when the job starts\n")
                #run_script.write("#SBATCH --mail-type=end         # email me when the job finishes\n")
            run_script.write("\n")
            run_script.write("# OpenMP controls\n")
            run_script.write("export OMP_NUM_THREADS=%s\n" % job.omp_num_threads)
            run_script.write("export MIC_ENV_PREFIX=MIC \n")
            run_script.write("export MIC_OMP_NUM_THREADS=%s\n" % job.mic_omp_num_threads)
            run_script.write("export MIC_KMP_AFFINITY=%s\n" % job.mic_affinity)
            run_script.write("\n")
            run_script.write("make .exe # Construct executable \n")
            run_script.write("\n") 
            run_script.write("# Run command\n")
            run_script.write(run_cmd)
            run_script.write("\n")
            if int(job.prefix) == 0:  
                run_script.write("# Plot command\n")
                run_script.write(plot_cmd)
            else: 
                run_script.write("# Plot command\n")
                temp_cmd = "#" + plot_cmd
                run_script.write(temp_cmd)

            run_script.write("\n")  
            run_script.write("# Extract Maximum Surge \n") 
            run_script.write(gauge_cmd)
            run_script.write("\n")
            #run_script.write("# Remove output files \n") 
            #run_script.write(remove_cmd)  

            run_script.close()
            
            
            # Submit job to queue
            subprocess.Popen("sbatch %s > %s" % (run_script_path, log_path),
                                                 shell=True).wait()
            

        # -- All jobs have been started --
            
    

    def process(self): 
        
        num_jobs = len(self.jobs)
        job = self.jobs[0] 
        process_script_name = ''.join((job.name, "_process.sh"))
        process_script_dir = os.path.join(self.base_path, "MaxSurge") 
        process_script_path = os.path.join(process_script_dir, process_script_name)
        process_script_log = ''.join((job.name, "_process", "_log.txt"))
        process_script_log_path = os.path.join(process_script_dir, process_script_log)
       

        if not os.path.exists(process_script_dir): 
            os.mkdir(process_script_dir) 

        return_period_program = os.path.join(self.base_path, "return_period.py") 
        process_cmd = "python %s %s %s %s" %(return_period_program,  
                                             self.base_path,
                                             job.name,
                                             process_script_dir)   
         
        
        # Write slurm run script to collect and process all max gauge data 
        process_script = open(process_script_path, 'w')

        process_script.write("#!/bin/sh\n")
        process_script.write("#SBATCH --account apam        # Job account\n"      )
        process_script.write("#SBATCH -J ProcessMaxGauges   # Job name\n"         )     
        process_script.write("#SBATCH -c 10"                                      )
        process_script.write("#SBATCH -t 1:30:00             # run time\n"        )  
        process_script.write("#SBATCH --mem-per-cpu=15gb     # memory/cpu core\n" )
        process_script.write("#SBATCH --nodes=1              # nodes needed\n "   )
        if self.email is not None:
            process_script.write("#SBATCH --mail-user=%s \n" % self.email )
            process_script.write("#SBATCH --mail-type=begin       # email me when the job starts\n")
            process_script.write("#SBATCH --mail-type=end         # email me when the job finishes\n")
        process_script.write("# Run command\n")
        process_script.write(process_cmd)
        process_script.write("\n") 

        process_script.close()
        
            
        # Submit job to queue
        subprocess.Popen("sbatch %s > %s" % (process_script_path, process_script_log_path),
                                                 shell=True).wait()

