AGrader
=======

Semi-automated CLI assignment grading solution designed primarily for running code.  Can interface with GoogleDocs and send e-mail to students with grades and customized messages.

Authored by Kyle Benson 2012

Distributed under the GNU Public License version 3.0 or the latest version.

Using GData Spreadsheet service
-----------------
You'll need to get credentials via OAuth2.  This requires you to create
a Google APIs project, enable Drive in it, get client credentials, and
then obtain a token via the following steps (using ipython) or by using the
gdata_creds.py helper script:

```
from oauth2client.client import flow_from_clientsecrets
flow = flow_from_clientsecrets('/path/to/gdata_creds.json', scope='https://spreadsheets.google.com/feeds', redirect_uri='http://localhost')
auth_uri = flow.step1_get_authorize_url()
print auth_uri
# use this auth_uri to navigate to a webpage in your browser where you agree to
# some terms and authorize this project. Copy the code that is in the redirected URL.
credentials = flow.step2_exchange('pasteTheCodeHere')
# now we save the credentials to a file for loading later into AGrader
# NOTE: you may need to specify the credentials file via the argument --gdata_creds
from oauth2client.file import Storage
storage = Storage('/path/to/.gdata.creds')
storage.put(credentials)
```

NOTE: see the following links for more details:
https://developers.google.com/api-client-library/python/guide/aaa_oauth
https://code.google.com/a/google.com/p/apps-api-issues/issues/detail?id=3851#c2
