#! /bin/bash
find . -type d -name "bin" -print | xargs -n 1 -I folder find folder -name "*.class" | xargs rm
