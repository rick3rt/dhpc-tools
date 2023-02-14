## install python packages dependencies locally

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

## symbolic links

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

## Demo

```
mysbatch test.sbatch
mysqueue
mysqueue -j 0 -c # cancel the 0th job in the list
```
