# Gdata Gradebook connector class
# @author: Kyle Benson
# (c) Kyle Benson 2012

from BaseGradebook import BaseGradebook
from threading import Thread

class GdataSpreadsheet(BaseGradebook, Thread):
    '''Provides interaction with Google docs spreadsheets as an external gradebook service.'''

    def __init__(self, ui, args=None):
        super(GdataSpreadsheet, self).__init__(ui)
        Thread.__init__(self)

        self.rowIndexMap = {}

        #TODO: put this stuff in base UI
        if args:
            self.primaryKey = args.submission_key
            self.spreadsheetName = args.assignment_key
            self.username = args.username
        else:            
            self.primaryKey = 'ucinetid'
            self.spreadsheetName = 'ICS23-Lab3-grades'
            self.username = 'kebenson@uci.edu'

        self.username = self.ui.promptStr('Enter google docs user info (default: %s): ' % self.username,
                                          default=self.username)
        self.password = self.ui.promptPassword('Enter password for ' + self.username + ': ')
        import gdata.spreadsheet.service as service
        self.service = service

        self.start()


    def run(self):
        '''Logs into Gdocs and gets the specified worksheet etc.'''
        self.gd_client = self.service.SpreadsheetsService() # prepend: gdata.spreadsheet.
        self.gd_client.email = self.username
        self.gd_client.password = self.password
        self.gd_client.ProgrammaticLogin()

        docs = self.gd_client.GetSpreadsheetsFeed()
        spreads = []

        #Get correct spreadsheet
        for i in docs.entry: spreads.append(i.title.text)
        spread_number = None
        for i,j in enumerate(spreads):
            if j == self.spreadsheetName: spread_number = i
        if spread_number == None:
            print "Error downloading gradebook from Google Spreadsheet. spread_number is None"
            exit

        #Get correct worksheet feed, then get first tab
        key = docs.entry[spread_number].id.text.rsplit('/', 1)[1]
        feed = self.gd_client.GetWorksheetsFeed(key)
        wksht_id = feed.entry[0].id.text.rsplit('/', 1)[1]
        self.gdoc_feed = self.gd_client.GetListFeed(key,wksht_id)


    def submitGrades(self, grades, key):
        self.join()
        self.gd_client.UpdateRow(self.gdoc_feed.entry[self.rowIndexMap[key]],grades)

    def getGrades(self, key):
        ###  TODO: build map once of key->index entries
        self.join()

        # Find the row corresponding to this KEY
        for i,entry in enumerate(self.gdoc_feed.entry):
            if entry.custom[self.primaryKey].text and entry.custom[self.primaryKey].text.strip().lower() == key:
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