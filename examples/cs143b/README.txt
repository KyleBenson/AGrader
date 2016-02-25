Steps to setup submissions for grading:

Download roster file from EEE (make sure you actually get the tabs when copy/pasting)
Modify it to remove everything after the '@' (I used vim with macros)
Upload this .tab file to Google Spreadsheets so you have 3 columns: student ID #, name, UCINetID
use the setup_submission_dirs.py script to move each [sid].txt file into a submission directory 
????? that expects ucinetid and we have sid need something else...
