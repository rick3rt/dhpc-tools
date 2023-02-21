#!/usr/bin/python3

import os
import subprocess
import pandas as pd
from datetime import datetime
from tabulate import tabulate


class Database:
    def __init__(self, columns, column_types):
        self.cols = columns
        self.data = []
        self.column_types = column_types

    def load_from_csv(self, filename):
        with open(filename, 'rt', encoding='utf-8') as f:
            line = f.readline()  # read header
            lines = f.readlines()
            for line in lines:
                row = line.split(',')
                for idx, c_type in enumerate(self.column_types):
                    row[idx] = c_type(row[idx])
                print(row)
                self.data.append(row)

    def save_to_csv(self, filename):
        with open(filename, 'wt', encoding='utf-8') as f:
            f.write(','.join(self.cols))
            f.write('\n')
            for row in self.data:
                f.write(','.join(row))

    def lookup_key(self, key):
        if key in self.cols:
            return self.cols.index(key)
        else:
            raise ValueError('Invalid key')

    def lookup_row(self, key, value):
        col_idx = self.lookup_key(key)
        value = self.column_types[col_idx](value)  # lets do string comparisons for now
        for row_idx, row in enumerate(self.data):
            if row[col_idx] == value:
                return row_idx
        return None
        # raise ValueError('Could not find row')

    def get_col(self, key):
        result = []
        col_idx = self.lookup_key(key)
        for row in self.data:
            result.append(row[col_idx])
        return result

    def get_item(self, key, index):
        return self.data[index][self.lookup_key(key)]

    def print_all(self):
        print(tabulate(self.data, headers=self.cols))

    def print_selection(self, keys):
        col_idx = [self.lookup_key(key) for key in keys]
        data = []
        for row in self.data:
            data.append(row[i] for i in col_idx)
        header = [self.cols[i] for i in col_idx]
        print(tabulate(data, headers=header))

    def sort_rows(self, key):
        col = self.get_col(key)
        print(col)
        sort_index = [i[0] for i in sorted(enumerate(col), key=lambda x:x[1], reverse=True)]
        self.data = [self.data[i] for i in sort_index]
        # and re index?
        icol = self.lookup_key('index')
        print(icol)
        if icol is not None:
            for ind, row in enumerate(self.data):
                row[icol] = ind

    def add_row(self, entry: dict, matchkey: str):
        # check if row is already in database
        append_row = False
        row_idx = self.lookup_row(matchkey, entry[matchkey])
        if row_idx is not None:
            # we have a known thing
            row = self.data[row_idx]
        else:
            row = [''] * len(self.cols)
            append_row = True
        for key, value in entry.items():
            col_idx = self.lookup_key(key)
            row[col_idx] = self.column_types[col_idx](value)
        if append_row:
            self.data.append(row)


def convert_slurm_time(time_str: str):
    try:
        dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
        return dt.strftime('%m-%d %H:%M')
    except ValueError:
        return ''


class SlurmManager:

    def __init__(self):
        self.database_folder = os.path.expanduser('~/.myslurm')
        self.database_file = 'jobs.csv'
        self.database_path = os.path.join(
            self.database_folder, self.database_file)

        self.columns = ["index", "JobID", "JobName", "WorkDir", "Partition",
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
        jobid = int(entry['JobID'])  # search for jobID
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
        if isinstance(cwd, str) and isinstance(outfile, str):
            return os.path.join(cwd, outfile)
        else:
            return ''

    def get_jobindex(self, jobid):
        return self.database.index[self.database['JobID'] == jobid][0]  # get index

    def get_jobid(self, index):
        return int(self.database["JobID"].loc[index])

    def get_outfile_id(self, jobid):
        return self.get_outfile(self.get_jobindex(jobid))

    def print_database(self, n=None):
        if n:
            print(self.database.loc[0:n - 1].to_markdown())
        else:
            print(self.database.to_markdown())

    def prettyprint_database(self, n=None):
        cols = ['JobID', 'JobName', 'State', 'Elapsed', 'Start']
        df = self.database
        if df.empty:
            print('Database empty...')
            return
        df = df[cols].loc[0:n - 1]
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

    cols = ["index", "JobID", "JobName", "WorkDir", "Partition",
            "Output", "State", "Elapsed", "Start", "End"]
    types = [int, int, str, str, str, str, str, str, str, str]
    db = Database(columns=cols, column_types=types)

    db.load_from_csv('test.csv')
    # db.save_to_csv('test_out.csv')

    print(db.lookup_key('JobID'))
    print(db.lookup_key('JobName'))
    print(db.lookup_row('JobID', 2065857))
    print(db.get_item('JobID', 1))

    db.print_selection(['index', 'JobID', 'Start'])

    db.print_all()

    e = {
        "JobID": 12312345,
        "JobName": "lalal"
    }
    db.add_row(e, "JobID")
    db.print_all()
    db.sort_rows("JobID")
    db.print_all()
