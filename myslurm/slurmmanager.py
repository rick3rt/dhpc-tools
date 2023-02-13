#!/usr/bin/python3

import os
import subprocess
import pandas as pd
from datetime import datetime


def convert_slurm_time(time_str: str):
    dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
    return dt.strftime('%m-%d %H:%M')


class SlurmManager:

    def __init__(self):
        self.database_folder = 'data'
        self.database_file = 'jobs.csv'
        self.database_path = os.path.join(
            self.database_folder, self.database_file)

        self.columns = ["JobID", "JobName", "WorkDir", "Partition",
                        "Output", "State", "Elapsed", "Start", "End"]
        self.column_types = [int, str, str, str, str, str, str, str, str]
        self.database = None
        self.load_database()

    def create_database(self):
        # , "State", "SubmitTime", "StartTime", "TimeLeft", "TimeLimit", "Nodes", "WorkDir"]

        if not os.path.exists(self.database_folder):
            os.mkdir(self.database_folder)
        self.database = pd.DataFrame(columns=self.columns)

    def load_database(self):
        if not os.path.isfile(self.database_path):
            print("No Database found, creating empty one. ")
            self.create_database()
            self.save_database()
        else:
            # print("Load Database")
            dtypes = dict(zip(self.columns, self.column_types))
            self.database = pd.read_csv(
                self.database_path, index_col=0, dtype=dtypes)

    def save_database(self):
        self.database.to_csv(self.database_path)

    def update_database(self, entry: dict):
        df = self.database
        jobid = entry['JobID']  # search for jobID
        idx = df.index[df['JobID'] == jobid]  # get index
        if idx.empty:
            # can append entry as new row cause job is unknown
            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
        else:
            # job is known, update data with data from entry
            for key, value in entry.items():
                df.loc[idx, [key]] = value

        # sort dataframe based on jobid
        df = df.astype({'JobID': 'int'})
        self.database = df.sort_values(
            by=['JobID'], ascending=False, ignore_index=True)

    def register_job(self, jobid: int, jobname: str, workdir: str, partition: str, output: str):
        entry = {
            "JobID": jobid,
            "JobName": jobname,
            "WorkDir": workdir,
            "Partition": partition,
            "Output": output,
        }
        self.update_database(entry)
        self.save_database()
        print(f'Registered job {jobid}.')

    def update_job(self, entry: dict):
        self.update_database(entry)

    def update_job_info(self):
        fields_to_get = ["JobID", "JobName", "Partition",
                         "State", "Elapsed", "Start", "End"]
        fields_str = ",".join(fields_to_get)
        args = ['sacct', '-u', os.getlogin(),
                f'--format={fields_str}', '-n', '-X', '-P']

        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            print("ERR: ", err)

        out = out.decode(encoding='utf-8')
        entries = [e.split('|') for e in out.splitlines()]
        for e in entries:
            d = dict(zip(fields_to_get, e))
            d['Start'] = convert_slurm_time(d['Start'])
            d['End'] = convert_slurm_time(d['End'])
            self.update_database(d)

    def get_outfile(self, index):
        cwd = self.database["WorkDir"].loc[index]
        outfile = self.database["Output"].loc[index]
        return os.path.join(cwd, outfile)

    def print_database(self, n=None):
        if n:
            print(self.database.loc[0:n-1].to_markdown())
        else:
            print(self.database.to_markdown())

    def prettyprint_database(self, n=None):
        cols = ['JobID', 'JobName', 'State', 'Elapsed', 'Start']
        df = self.database
        df = df[cols].loc[0:n-1]
        print(df.to_markdown())

    def prettyprint_entry(self, idx):
        cols = ['JobID', 'JobName', 'State', 'Elapsed', 'Start']
        df = self.database[cols].loc[idx]
        print(df.to_markdown())  # TODO: rotate dataframe
        # print(df.transpose())


if __name__ == "__main__":
    # fields_to_get = ["JobID", "JobName", "Partition",
    #                  "State", "Elapsed", "Start", "End"]
    # fields_str = ",".join(fields_to_get)
    # args = ['sacct', '-u', os.getlogin(),
    #         f'--format={fields_str}', '-n', '-X', '-P']

    # p = subprocess.Popen(args, stdout=subprocess.PIPE)
    # out, err = p.communicate()
    # if err:
    #     print("ERR: ", err)

    # out = out.decode(encoding='utf-8')
    # entries = [e.split('|') for e in out.splitlines()]
    # for e in entries:
    #     d = dict(zip(fields_to_get, e))
    #     d['Start'] = convert_slurm_time(d['Start'])
    #     d['End'] = convert_slurm_time(d['End'])

    # exit(0)
    # for entry in entries:
    #     entry = entry.split('|')
    #     print(entry)

    pass
