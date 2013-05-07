#!/bin/bash
find sources/ -type f | sort | xargs -L 1 less
