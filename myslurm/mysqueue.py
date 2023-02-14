#!/usr/bin/python3

import os
import argparse
from slurmmanager import SlurmManager


if __name__ == '__main__':
    # setup parser
    parser = argparse.ArgumentParser(
        description='Submit a job through a python wrapper to manage jobs.')
    parser.add_argument('-l', '--list',
                        help="List running jobs", action="store_true")
    parser.add_argument('-j', '--jobindex',
                        help='Select job by index', type=int)
    parser.add_argument('-J', '--jobid',
                        help='Select job by jobid', type=int)
    parser.add_argument('-o', '--output',
                        help='Show log file for selected job', action="store_true")
    parser.add_argument('-t', '--tail',
                        help='Tail log file for selected job (default is cat)', action="store_true")
    parser.add_argument('-n', '--numjobs',
                        help='Number of jobs to display', type=int, default=10)
    parser.add_argument('-c', '--cancel',
                        help='Cancel the selected job', action="store_true")

    args = parser.parse_args()
    SM = SlurmManager()
    SM.update_job_info()  # get latest info
    SM.save_database()  # save latest info

    # select a job
    if args.list:
        SM.prettyprint_database(args.numjobs)

    elif args.output:
        if args.jobindex is None:
            print('Specify which job to show the output for using -j/-J:')
            parser.print_help()
        SM.prettyprint_entry(args.jobindex)
        outfile = SM.get_outfile(args.jobindex)
        # cat/tail outfile
        cmd = "cat"
        if args.tail:
            cmd = "tail"
        if os.path.isfile(outfile):
            os.system(f'{cmd} {outfile}')
        else:
            print(f"Could not find output file\n\t{outfile}")

    elif args.cancel:
        if args.jobindex is not None:
            jobid = SM.get_jobid(args.jobindex)
        else:
            jobid = args.jobid
        print(f'Cancelling {jobid}')
        os.system(f'scancel {jobid}')

    else:
        SM.prettyprint_database(args.numjobs)
