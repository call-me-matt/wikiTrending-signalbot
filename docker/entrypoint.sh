#!/bin/sh

timestamp=`date -I"seconds"`
echo "$timestamp Signal-bot started!"

cd /app/trending/
python3 wikiScanner.py &
python3 signalNotifier.py
