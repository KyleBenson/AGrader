# Gdata Gradebook connector class
# @author: Kyle Benson
# (c) Kyle Benson 2012

from AGrader.Gradebook.BaseGradebook import BaseGradebook
from threading import Thread

# defaults that don't really do anything, just serve as flags to show the values are unset
DEFAULT_USERNAME='some_user@gmail.com'
DEFAULT_SPREADSHEET='grades_sheet'

class GdataSpreadsheet(BaseGradebook, Thread):
    '''Provides interaction with Google docs spreadsheets as an external gradebook service.'''

    def __init__(self, ui, args=None):
        super(GdataSpreadsheet, self).__init__(ui)
        Thread.__init__(self)

        self.rowIndexMap = {}

        #TODO: put this stuff in base UI
        if args:
            self.args = args
            self.primaryKey = args.submission_key
            self.spreadsheetName = args.assignment_key
            self.username = args.username
            self.password = args.passwd
        else:
            #make some args
            self.args = lambda:0
            self.args.verbose = True

            self.primaryKey = 'ucinetid'
            self.spreadsheetName = DEFAULT_SPREADSHEET
            self.username = DEFAULT_USERNAME

        self.promptLoginInfo()

        import gdata.spreadsheet.service as service
        self.service = service

        self.start()

    def promptLoginInfo(self):
        '''
        Only prompt if it hasn't been explicitly specified.
        '''
        # OAuth2 login now required
        if self.args.verbose:
            self.ui.notify("No longer using username/password credentials!  Skipping that step...")
        return

        if self.username == DEFAULT_USERNAME:
            self.username = self.ui.promptStr('Enter google docs user info (default: %s): ' % self.username,
                                              default=self.username)
        if self.args.passwd is None:
            self.password = self.ui.promptPassword('Enter password for ' + self.username + ': ')

    def run(self):
        '''Logs into Gdocs and gets the specified worksheet etc.'''
        success = False

        while not success:
            self.gd_client = self.service.SpreadsheetsService() # prepend: gdata.spreadsheet.
            # login via username/password appears to no longer be supported.
            # OAuth2 is now required
            #self.gd_client.email = self.username
            #self.gd_client.password = self.password

            # this requires using a browser to authorize the app, can do this
            # via command line and just store the credentials for later
            # retrieval instead....

            #from oauth2client.client import flow_from_clientsecrets
            #credentials = flow_from_clientsecrets(self.args.gdata_creds, scope=["https://spreadsheets.google.com/feeds"])

            from oauth2client.file import Storage
            credStore = Storage(self.args.gdata_creds)
            credentials = credStore.get()
            self.gd_client.additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token}

            try:
                self.gd_client.ProgrammaticLogin()
                success = True
            except: #BadAuthentication:
                self.ui.notifyError("Invalid login info! Abort?")
                self.promptLoginInfo()

        docs = self.gd_client.GetSpreadsheetsFeed()
        spreads = []

        #Get correct spreadsheet
        for i in docs.entry: spreads.append(i.title.text)
        spread_number = None
        for i,j in enumerate(spreads):
            if self.args.verbose:
                self.ui.notify("Gradebook: Checking spreadsheet %s" % j)
            if j == self.spreadsheetName:
                spread_number = i
                if self.args.verbose:
                    self.ui.notify("Gradebook: Loading spreadsheet %s" % self.spreadsheetName)
                break

        if spread_number == None:
            self.ui.notifyError("Error downloading gradebook %s from Google Spreadsheet. spread_number is None" % self.spreadsheetName)

        #Get correct worksheet feed, then get first tab
        key = docs.entry[spread_number].id.text.rsplit('/', 1)[1]
        feed = self.gd_client.GetWorksheetsFeed(key)
        wksht_id = feed.entry[0].id.text.rsplit('/', 1)[1]
        self.gdoc_feed = self.gd_client.GetListFeed(key,wksht_id)


    def submitGrades(self, grades, key):
        try:
            self.join()

            # make sure each 'cell' submitted is a string
            try:
                grades = {k:str(v) for k,v in grades.iteritems()}
            except Exception as e:
                if self.args.verbose:
                    self.ui.notifyError(e)
                self.ui.notifyError("Couldn't convert submitted grade to a string for some reason. Gradebook.Gdata.submitGrades")

            self.gd_client.UpdateRow(self.gdoc_feed.entry[self.rowIndexMap[key]],grades)
        except AttributeError as e:
            self.ui.notifyError("Problem submitting grades for %s: %s\n%s" % (key, grades, e))

    def getGrades(self, key):
        '''Returns the gradebook row associated with the given student/group key.
        None if no valid key found.'''
        ###  TODO: build map once of key->index entries
        self.join()

        # Find the row corresponding to this KEY
        for i,entry in enumerate(self.gdoc_feed.entry):
            # check if this is the row we want
            # this first only checks if there's text here
            if entry.custom[self.primaryKey].text:
                key_value = entry.custom[self.primaryKey].text.strip().lower()
                if key_value != key:
                    continue

                if self.args.verbose >= 3:
                    self.ui.notify("Found record: " + key_value)

                self.rowIndexMap[key] = i

                #store dictionary for updating row later
                gradebook_row = {}
                for name,value in entry.custom.iteritems():
                    tmp = value.text
                    if tmp is not None:
                        tmp = tmp.strip()
                    gradebook_row[name] = tmp
                return gradebook_row

        if key not in self.rowIndexMap:
            self.ui.notifyError("ERROR: Key " + key + ' not found.')
            return None
