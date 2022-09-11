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

set -x

# APPDIR should be ./autobot
(cd $APPDIR/$TRAINDIR && python training.py --data=dataset/v1/q_data.csv --save-mode=model/simple_v1)