#!/usr/bin/python3

import pandas as pd
import os


class SlurmManager:

    def __init__(self):
        self.database_folder = 'data'
        self.database_file = 'jobs.csv'
        self.database_path = os.path.join(self.database_folder, self.database_file)

        self.database = None
        self.load_database()

    # setup autosave of database when class is destructed
    # def __del__(self):
    #     self.save_database()

    def create_database(self):
        # , "State", "SubmitTime", "StartTime", "TimeLeft", "TimeLimit", "Nodes", "WorkDir"]
        cols = ["JobID", "Name", "WorkDir", "Partition", "SubmitTime", "TimeLimit", "Output"]
        if not os.path.exists(self.database_folder):
            os.mkdir(self.database_folder)
        self.database = pd.DataFrame(columns=cols)

    def load_database(self):
        if not os.path.isfile(self.database_path):
            print("No Database found, creating empty one. ")
            self.create_database()
            self.save_database()
        else:
            self.database = pd.read_csv(self.database_path, index_col=0)

    def save_database(self):
        self.database.to_csv(self.database_path)

    def print_database(self):
        print(self.database.to_markdown())

    def register_job(self, jobid: int, name: str, workdir: str, partition: str,
                     submittime: str, timelimit: str, output: str):

        entry = {
            "JobID": jobid,
            "Name": name,
            "WorkDir": workdir,
            "Partition": partition,
            "SubmitTime": submittime,
            "TimeLimit": timelimit,
            "Output": output,
        }
        self.database = self.database.append(entry, ignore_index=True)
        self.save_database()
        print(f'Registered job {jobid}.')


if __name__ == "__main__":

    SM = SlurmManager()
    SM.create_database()
    SM.save_database()
    SM.print_database()
