#!/bin/bash
# Remember to run this with nohup!
# nohup .runtime/run.sh &>/dev/null &
pwd | grep -q .runtime
if [ "$?" -eq "0" ]; then
    cd ..
fi
python3 -m venv .venv
source .venv/bin/activate
fastapi run