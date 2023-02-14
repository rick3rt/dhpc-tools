# 

## syncfolder
Requirement: inotifynowait (not installed by default, need to install to home directory)
First download package
```
$ mkdir -p ~/downloads
$ yumdownloader --destdir ~/downloads inotify-tools
$ mkdir ~/packages
$ cd ~/packages&& rpm2cpio ~/downloads/<inotify-tools-filename>.rpm | cpio -id
```
Now setup .bashrc:
```
export PATH="$HOME/packages/usr/sbin:$HOME/packages/usr/bin:$HOME/packages/bin:$PATH"
export MANPATH="$HOME/packages/usr/share/man:$MANPATH"
L='/lib:/lib64:/usr/lib:/usr/lib64'
export LD_LIBRARY_PATH="$HOME/packages/usr/lib:$HOME/packages/usr/lib64:$L"
```




