#! /usr/bin/python

usage=\
'''
Summary: ./grade-labs.py projects_directory grading_comments_directory email_appendix_file

runs through all of the directories representing Eclipse projects in the directory specified ('.' by default) and (attempts to) run the project.

Between each project, it prompts the user for a grade of pass or fail (p or f button)
and then for a reason, which is mapped to any other key as defined by the entries in the directory 'grading-reasons' or arg2 if included.

A file for a grading reason follows the following format:
a single character for a keystroke on the first line
a message to be included in the grade email.

An optional 3rd argument provides a file from which the remainder of the email comes.  Use for announcements, general observations, refined directions, etc.
'''

show_profile = False
output_connector = None
USERNAME = 'kebenson@uci.edu'
SPREADSHEET_NAME = 'ICS21-Summer2012-grades-labexams'

from os import listdir, system, getcwd, chdir, getcwd
from os.path import isdir, join, split, exists
from sys import argv
from getpass import getpass

CRLF = '\r\n'

if len(argv) <= 1 or argv[1] in ['help', '--help', '-help', '-h', '-H']:
    print usage
    exit(0)

if len(argv) > 1:
    top_dir = argv[1]
else:
    top_dir = '.'

if len(argv) > 2:
    comments_dir = argv[2]
else:
    comments_dir = None

if len(argv) > 3:
    with open(argv[3]) as f:
        email_appendix = f.read()
else:
    email_appendix = None

#main_class = 'MusicArchive' if 'LabExam4' in argv[1] else 'Smiley'

#gather comments if requested
if comments_dir:
    comments = {}
    comments_files = []
    root = split(comments_dir)[0]
    for reason in listdir(comments_dir):
        comments_files.append(reason)

        with open(join(root,reason)) as f:
            key = f.readline().strip()
            message = f.read()
            comments[key] = messag

#load gradebook spreadsheet if requested
if output_connector:
    PASSWD = getpass('Enter password for ' + USERNAME + ': ')
    import gdata.spreadsheet.service
    gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    gd_client.email = USERNAME
    gd_client.password = PASSWD
    gd_client.ProgrammaticLogin()

    docs = gd_client.GetSpreadsheetsFeed()
    spreads = []

    #Get correct spreadsheet
    for i in docs.entry: spreads.append(i.title.text)
    spread_number = None
    for i,j in enumerate(spreads):
        if j == SPREADSHEET_NAME: spread_number = i
    if spread_number == None:
        print "Error downloading gradebook from Google Spreadsheet. spread_number is None"
        exit

    #Get correct worksheet feed
    key = docs.entry[spread_number].id.text.rsplit('/', 1)[1]
    feed = gd_client.GetWorksheetsFeed(key)
    wksht_id = feed.entry[0].id.text.rsplit('/', 1)[1]
    feed = gd_client.GetListFeed(key,wksht_id)

pwd = getcwd()

for folder in listdir(top_dir):
    folder = join(top_dir,folder)

    #make sure its an Eclipse (or some) project
    if not isdir(folder) or 'src' not in listdir(folder):
        if '.email' not in folder:
            print folder + " is not an Eclipse project!"
        continue

    #parse folder name
    email_name, sep, current_attempt_number = folder.rpartition('-')
    if current_attempt_number == '':
        print 'ERROR: ', folder, ' does not follow the naming convention!'
        continue
    current_attempt_number = int(current_attempt_number)

    lab_number, sep, email_name = email_name.rpartition('-')
    ucid = email_name
    email_name = join(top_dir,email_name + '.email')

    lab_number = split(lab_number)[1]
    if email_name == '.email' or not lab_number:
        print 'ERROR: ', folder, ' does not follow the naming convention!'
        continue
    #lab_number = int(lab_number)

    #print lab_number, email_name, current_attempt_number

    #collect stats from gradebook

    #Get correct row (if it exists) and save information
    row_index = None
    for i,entry in enumerate(feed.entry):
        if entry.custom['ucinetid'].text is None:
            break
        if entry.custom['ucinetid'].text.strip().lower() == ucid.strip().lower():
            row_index = i

            last_name = entry.custom['lastname'].text.strip()
            first_name = entry.custom['firstnameetc'].text.strip()
            full_name = first_name + ' ' + last_name
            stud_id = entry.custom['id'].text.strip()
            last_attempt_num = entry.custom['attempts' + (('_' + lab_number) if int(lab_number) > 1 else '')].text
            
            if not last_attempt_num:
                last_attempt_num = '0'
            else:
                last_attempt_num = last_attempt_num.strip()

            #store dictionary for updating row later
            gradebook_row = {}
            for name,value in entry.custom.iteritems():
                tmp = value.text
                if tmp is not None:
                    tmp = tmp.strip()
                gradebook_row[name] = tmp
            #print gradebook_row
            break

    if row_index is None:
        print "ERROR: Student " + ucid + ' not found.'
        continue

    #print full_name, row_index, stud_id, ucid

    #check if this attempt has already been graded
    if exists(email_name) or exists(email_name + '.sent') and current_attempt_number <= int(last_attempt_num):
        continue
    email = [full_name + ',', CRLF + 'This is your grade report for Lab Exam #' + str(lab_number) + CRLF]

    chdir(folder)

    #TODO: figure out the main_class!!!

    system('javac -cp ./lib:./src -d bin src/*')
    system('java -cp ./lib:./src:./bin ' + main_class)

    #give option for viewing source code
    if raw_input("View source files? y/n? ") == 'y':
        system('find src \( -iname "*.java" \'!\' -name Smiley.java \'!\' -name MusicArchive.java \) -exec less \'{}\' +')
        if 'LabExam4' in argv[1]:
            if not exists('index.txt'):
                print 'No index.txt file!'
                
            else:
                with open('index.txt') as musicIndex:
                    musicLines = musicIndex.readlines()
                    if len(musicLines) < 2:
                        print "index.txt file EMPTY!"
                        pass
                    else:
                        for i in range(1, len(musicLines)):
                            if musicLines[i] == musicLines[i-1]:
                                print 'DUPLICATE item!'
                                system('less index.txt')
                                break
                            elif musicLines[i] < musicLines[i-1]:
                                print 'NOT alphabetized!'
                                system('less index.txt')
                                break
                        else:
                            print 'index.txt aplhabetized!'

    #prompt for grade
    grade = None
    while grade is None:
        grade = raw_input("Did " + ucid + " pass? y or n, p or f\n")
        if '+' in grade:
            # remove the +
            grade = grade.translate(None, '+')
            personal_message = raw_input("Type your personal message then hit enter:\n") + '\n'

        if grade is not None and grade not in 'ynpf':
            print "You must type one letter of y, n, p, or f"
            grade = None

            

    if grade in 'yp':
        passed = True
    else:
        passed = False

    #prompt for reason
    reason = None
    personal_message = None
    while not passed and reason is None:
        reason = raw_input("Why not?\nOptions are: " + str(comments.keys()) + "\nAdd a + to include a personalized message on a separate line. You can also specify only + for just a personalized reason.\nOr press 'h' for help.\n")
        if '+' in reason:
            # remove the +
            reason = reason.translate(None, '+')
            personal_message = raw_input("Type your personal message then hit enter:\n") + '\n'

        # Allow blank reason if a personal message is specified
        if reason == '' and personal_message:
            reason = 'skip'

        elif reason not in comments.keys()+['skip'] or reason == 'h':
            if reason == 'h':
                print 'The possible grading reasons are chosen from the single letters: ' + str(comments.keys()) + '\nThey were pulled from the files: ' + str(comments_files)
            else:
                print "You must type one letter of " + str(comments.keys())
            reason = None

    #write whether they passed or not
    if passed:
        email.append("You passed this lab exam.  Keep up the good work!")
        gradebook_row['labexam' + lab_number] = 'P'
    else:
        email.append('You did not pass this lab exam for the following reason:')
        if reason != 'skip':
            email.append(comments[reason])
        if personal_message:
            email.append(personal_message)
        email.append('I will be holding a retake session soon in which you can attempt this lab exam again.')
        gradebook_row['labexam' + lab_number] = 'N'

    email.append('This was your attempt #' + str(current_attempt_number))

    #Gdocs does this funny thing where it appends a '_' and then a number if a column repeats, but only after the first occurrence and starting at 2
    gradebook_row['attempts' + (('_' + lab_number) if int(lab_number) > 1 else '')] = str(current_attempt_number)
    email.append(CRLF)

    if show_profile:
        email.append('I have the following information about you on file. If a field shows up as \'Fill In Here\', that means that you did not provide it in your submission.  Please reply to this email with any corrections:\n')
        email.append('NAME: ' + full_name)
        email.append('STUDENT ID: ' + stud_id)
        email.append('UCINET ID: ' + ucid + CRLF)
    
    if email_appendix:
        email.append(email_appendix)

    chdir(pwd)

    #write email
    with open(email_name, 'w') as f:
        email = CRLF.join(email)
        #print email_name
        f.write(email)

    #update gradebook row
    gd_client.UpdateRow(feed.entry[row_index],gradebook_row)
    
