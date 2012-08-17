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
import shutil

if len(argv) < 3:
    print usage
    exit(0)

top_dir = argv[1]
if len(argv) > 3:
    fromAddress = argv[3]
else:
    fromAddress = 'kebenson@ics.uci.edu'

smtp = SMTP('smtp.ics.uci.edu')

for filename in [join(top_dir,i) for i in listdir(top_dir) if i.endswith('.email')]:
    recipient = split(filename)[1].replace('.email','') + '@uci.edu'
    
    f = open(filename)
    msg = f.read()
    f.close()
    
    shutil.move(filename, filename + '.sent')

    msg = MIMEText(msg)
    msg['Subject'] = argv[2]
    msg['From'] = fromAddress
    msg['To'] = recipient
    msg['Bcc'] = fromAddress
    msg['Reply-to'] = fromAddress
    
    smtp.sendmail(fromAddress, [recipient], msg.as_string())

smtp.quit()
