#!/usr/bin/env bash

SRCDIR="src"
BINDIR="bin"
TRAINDIR="training"
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
APPDIR=$( cd -P "$( dirname "$DIR" )" >/dev/null 2>&1 && pwd ) 


# create log folder
(mkdir $APPDIR/log > /dev/null 2>&1)

# disable Tensorflow debugging message


# change working directory and run uvicorn
# (cd $APPDIR$SRCDIR && uvicorn main:app --workers 1)

# change working directory and run gunicorn
(cd $APPDIR/$SRCDIR && gunicorn --config $APPDIR/$BINDIR/gunicorn.conf.py)