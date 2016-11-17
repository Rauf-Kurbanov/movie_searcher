#! /usr/bin/bash
find . -type f -name '*.txt' -exec cat {} + >> `dirname "$0"`/full.csv
