# How to use
To submit a batch file, use the command `mysbatch`. Example batch file `test_matlab.sbatch`:
```
#!/bin/sh

#SBATCH --job-name=test_matlab
#SBATCH --partition=compute
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1G
#SBATCH --cpus-per-task=2
#SBATCH --account=research-as-imphys
#SBATCH --output=slog/%x-%j.out

# Your job commands go below here
module load 2022r2
module load matlab

srun matlab -nodesktop -r "for k=1:1000; fprintf('%i seconds have passed\n',k); pause(1); end; exit()"
```
Submit:
```
$ mysbatch test_matlab.sbatch
Registered job 2013021.
```
Now to poll the status of running jobs, use `mysqueue`
```
$ mysqueue
|    |   JobID | JobName      | State               | Elapsed   | Start       |
|---:|--------:|:-------------|:--------------------|:----------|:------------|
|  0 | 2013021 | test_matlab  | RUNNING             | 00:00:26  | 02-14 14:06 |
|  1 | 2012998 | test_matlab  | CANCELLED by 551413 | 00:00:48  | 02-14 13:58 |
|  2 | 2012979 | test_matlab  | TIMEOUT             | 00:05:01  | 02-14 13:46 |
```
Cancel a job with the `--cancel` (short `-c`) flag, 
```
$ mysqueue -j 0 -c
Cancelling 2013021
```
To view the output file of job 2013021 (argument `--output` or short `-o`), we 
can use the index in the list (specified as `--jobindex` or short `-j`) as follows: 
```
$ mysqueue -j 0 -o
|         | 0           |
|:--------|:------------|
| JobID   | 2013021     |
| JobName | test_matlab |
| State   | RUNNING     |
| Elapsed | 00:01:40    |
| Start   | 02-14 14:06 |
MATLAB is selecting SOFTWARE OPENGL rendering.

                            < M A T L A B (R) >
                  Copyright 1984-2021 The MathWorks, Inc.
                  R2021b (9.11.0.1769968) 64-bit (glnxa64)
                             September 17, 2021


To get started, type doc.
For product information, visit www.mathworks.com.

1 seconds have passed
2 seconds have passed
3 seconds have passed
4 seconds have passed
5 seconds have passed
6 seconds have passed 
```
To only see the last lines in the outfile, you can use the `--tail` (`-t`)
option:
```
$ mysqueue -otj 0
|         | 0           |
|:--------|:------------|
| JobID   | 2013021     |
| JobName | test_matlab |
| State   | RUNNING     |
| Elapsed | 00:03:49    |
| Start   | 02-14 14:06 |
202 seconds have passed
203 seconds have passed
204 seconds have passed
205 seconds have passed
206 seconds have passed
207 seconds have passed
208 seconds have passed
209 seconds have passed
210 seconds have passed
211 seconds have passed
```

# Setup

## Install python packages dependencies locally

Default python is 3.6.8 located at `/usr/bin/python`. To install `pandas` for
this python version locally locally, run

```
mkdir -p /scratch/${USER}/.local
ln -s /scratch/${USER}/.local $HOME/.local
python -m pip install --user pandas tabulate
```

See
https://doc.dhpc.tudelft.nl/delftblue/Python/#install-your-own-packages-locally
for details.

## Create symbolic links

First make python files executable
```
chmod +x mysbatch.py
chmod +x mysqueue.py
```
Then make symbolic links in `~/.local/bin`
```
ln -s <path to dhpc-tools>/myslurm/mysbatch.py ~/.local/bin/mysbatch
ln -s <path to dhpc-tools>/myslurm/mysqueue.py ~/.local/bin/mysqueue
```
