#! /usr/bin/python
usage = \
'''
Summary: ./sendgrades.py email_directory subject from_address

Sends the emails contained in email_directory to the user (@uci.edu) specified in each
email filename.  For example, the file kebenson.email will be sent to kebenson@uci.edu

The from address is used as the from and reply-to addresses for the email.
'''

from sys import argv
from os import listdir
from os.path import join, split
from smtplib import SMTP
from email.MIMEText import MIMEText

if len(argv) < 4:
    print usage
    exit(0)

top_dir = argv[1]

for filename in [join(top_dir,i) for i in listdir(top_dir) if i.endswith('.email')]:
    recipient = split(filename)[1].replace('.email','') + '@uci.edu'
    
    f = open(filename)
    msg = f.read()
    f.close()
    
    msg = MIMEText(msg)
    msg['Subject'] = argv[2]
    msg['From'] = argv[3]
    msg['To'] = recipient
    msg['Bcc'] = argv[3]
    msg['Reply-to'] = argv[3]
    
    #print msg

    s = SMTP('smtp.ics.uci.edu')
    s.sendmail('kebenson@ics.uci.edu', [recipient], msg.as_string())
    s.quit()
