#!/bin/bash
cd /mnt/c/Users/Chris\ Norris-Jones/Desktop/Projects/virtenv/rssparser/bin
.  ./activate
cd ../../../rssparser
python pythonparser.py -u
deactivate
