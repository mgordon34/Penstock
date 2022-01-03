#!/bin/bash

HOME=/home/matt
BINDIR=$HOME/git/stonks/penstock
VENVDIR=$HOME/git/stonks/.venv

cd $BINDIR
source $VENVDIR/bin/activate
python $BINDIR/injest_live_data.py
