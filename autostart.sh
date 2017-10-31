#!/bin/bash
until python3.6 main.py; do
    echo "'main.py' crashed with exit code $?. Restarting..." >&2
    sleep 1
done
