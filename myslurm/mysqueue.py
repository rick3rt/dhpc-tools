#!/usr/bin/python3

import os
import argparse
import sys
import subprocess
from datetime import datetime
from slurmmanager import SlurmManager


def submit_job(sbatch_args_list: list):
    sbatch_args_list.insert(0, 'sbatch')  # add sbatch command
    p = subprocess.Popen(sbatch_args_list, stdout=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        print("ERR: ", err)
    # get jobid from out:
    jobid = [int(s) for s in out.split() if s.isdigit()][0]
    return jobid


if __name__ == '__main__':
    # setup parser
    parser = argparse.ArgumentParser(
        description='Submit a job through a python wrapper to manage jobs.')
    parser.add_argument('-c', '--cpus-per-task', help='CPUs per task', type=int)
    parser.add_argument('-J', '--job-name',
                        help="Specify a name for the job allocation.", type=str)
    parser.add_argument('-p', '--partition',
                        help="Request specific partition for job execution.", type=str)
    parser.add_argument('-t', '--time',
                        help="Request specific partition for job execution.", type=str)
    parser.add_argument('-o', '--output', help='log file location', type=str)

    # get working directory for
    cwd = os.getcwd()
    print(cwd)

    # scan input arguments or sbatch file for
    sbatch_file = sys.argv[-1]
    with open(sbatch_file, 'rt', encoding='utf-8') as f:
        sbatch_commands = [line for line in f.readlines() if '#SBATCH' in line]
        sbatch_args = [arg.strip('#SBATCH ').rstrip() for arg in sbatch_commands]
        # sbatch_args = " ".join(sbatch_args)

    # collect args from command line and that are in sbatch file
    original_args = sys.argv.copy()[1:]  # everything except the python scriptname
    all_args = sys.argv.copy()
    all_args.extend(sbatch_args)
    args, extra_args = parser.parse_known_args(all_args)  # and parse

    # submit job
    jobid = submit_job(original_args)

    # format outputfile
    output_file = args.output
    print(output_file)
    output_file = output_file.replace('%x', args.job_name)
    print(output_file)
    output_file = output_file.replace('%j', str(jobid))
    print(output_file)

    # and update SlurmManager database
    SM = SlurmManager()
    SM.register_job(jobid=jobid, name=args.job_name, workdir=cwd,
                    partition=args.partition, submittime=datetime.now(),
                    timelimit=args.time, output=output_file)
