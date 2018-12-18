#!/bin/bash

FAILS=0

while true
do
  sleep 0.5
  python3.6 main.py
  EXIT=$?
  ((FAILS++))

  if [[ $FAILS -gt 10 ]]
  then
    echo "[$(date)] failed to many times. aborting ..."
    exit 1
  fi

  echo "[$(date)] bot exited with code $EXIT. restarting ..."

done