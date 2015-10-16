#!/bin/bash
# runs agrader for this assignment, passing these config parameters to the CLI

# Change your Google Drive user info here if using GData Gradebook
GMAIL_ACCOUNT='username@uci.edu'
GMAIL_PASSWORD='SECRET_PASSWORD'

# I have an alias to run AGrader
#AGRADER_PATH='agrader'
# that doesn't work in a script....
AGRADER_PATH='~/repos/AGrader/agrader.py'

# Assignment related stuff
SPREADSHEET='CS143B-Project3-grades'
ASSIGNMENT_DIR='/home/kebenson/scratch/grading/cs234b/project2'

# run command, adding any extra CLI args to agrader
COMMAND="$AGRADER_PATH --assignment_key $SPREADSHEET --username $GMAIL_ACCOUNT --passwd $GMAIL_PASSWORD -d $ASSIGNMENT_DIR $@"
#echo $COMMAND
eval $COMMAND
