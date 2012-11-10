# Gdata Gradebook connector class
# @author: Kyle Benson
# (c) Kyle Benson 2012

from BaseGradebook import BaseGradebook

class GdataSpreadsheet(BaseGradebook):
    '''Provides interaction with Google docs spreadsheets as an external gradebook service.'''

    def __init__(self, workspace):
        self.ui = workspace.ui
        self.rowIndexMap = {}

        self.primaryKey = 'ucinetid'
        self.spreadsheetName = 'ICS23-Lab3-grades'
        self.username = 'kebenson@uci.edu'

        new_user = self.ui.promptStr('Enter google docs user info (default: %s): ' % self.username)
        self.password = self.ui.promptPassword('Enter password for ' + self.username + ': ')
        import gdata.spreadsheet.service
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
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
        self.gd_client.UpdateRow(self.gdoc_feed.entry[self.rowIndexMap[key]],grades)

    def getGrades(self, key):
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
