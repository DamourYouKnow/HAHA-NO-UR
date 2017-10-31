until bot.py; do
    echo "'bot.py' crashed with exit code $?. Restarting..." >&2
    sleep 1
done
