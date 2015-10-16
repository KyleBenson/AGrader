#!/usr/bin/python

import os.path

from oauth2client.client import flow_from_clientsecrets
flow = flow_from_clientsecrets(os.path.join(os.path.expanduser('~'), '.gdata_creds.json'), scope='https://spreadsheets.google.com/feeds', redirect_uri='http://localhost')
auth_uri = flow.step1_get_authorize_url()
print auth_uri
theCode = raw_input("Navigate to the above URL and then enter the code pulled from the redirect URL: ")
# use this auth_uri to navigate to a webpage in your browser where you agree to
# some terms and authorize this project. Copy the code that is in the redirected URL.
credentials = flow.step2_exchange(theCode)
# now we save the credentials to a file for loading later into AGrader
# NOTE: you may need to specify the credentials file via the argument --gdata_creds
from oauth2client.file import Storage
storage = Storage(os.path.join(os.path.expanduser('~'), '.gdata.creds'))
storage.put(credentials)
