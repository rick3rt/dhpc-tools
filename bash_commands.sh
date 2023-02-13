# cat /home/rwaasdorp1/scratch/repos/dhpc-tools/bash_commands.txt

# data from NIN to dHPC
rsync -r -e ssh waasdorp@192.87.10.26:~/data/RickWaasdorpTmp/05-10-2022/* .

# data from dHPC to NIN 
rsync -r -e ssh SRC waasdorp@192.87.10.26:/REMOTE_PATH

# 

