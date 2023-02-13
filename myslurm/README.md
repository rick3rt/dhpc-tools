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



