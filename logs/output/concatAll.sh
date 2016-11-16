#! /usr/bin/bash

find . -type f -name '*.txt' -exec cat {} + >> full.csv
