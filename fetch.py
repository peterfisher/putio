__author__ = 'peter@phyn3t.com'

import putio
import os
import httplib2
import ConfigParser
import sys

class fetch:

    def getAllItems(self):
        """Get entire put.io account and and save it to a dict called contents.
            This function will iterate over your entire put.io account and
            download all files. It saves the following attribuites to the
            dictionary contents: item name, parent item ID, item size, and
            download url.
         """

        control = []

        for folder in self.API.get_items():
            control.append(folder.id)

        while control.__len__() > 0:
            try:
                for item in self.API.get_items(parent_id=control.pop()):
                    print("Getting content for: " + item.name)
                    if item.type == "folder":
                        control.insert(0,item.id)
                    else:
                        self.contents[item.id] = {
                            'name': item.name, 'parentID': item.parent_id,
                            'size': item.size, 'uri': item.download_url
                        }
            except putio.PutioError as err:
                print("Can't get content for Directory")
                pass
        return self.contents


    def putioPath(self, itemID=None):
        """Figures out the full path to a file on Put.io

        itemID equals the id of the file which you want to determine the path.
        returns a string that contains the path of the file /foo/bar.txt
        """

        path = self.API.get_items(id=itemID)[0].name

        while (True):
            itemID = self.API.get_items(id=itemID)[0].parent_id
            if itemID == "0":
                break
            else:
                path = self.API.get_items(id=itemID)[0].name + "/" + path
        return  self.dlLocation + path

    def createLocalDirectory(self, file=None):
        """Check whether local directory tree exists. Create if not.
        """

        if file == None:
            raise ValueError("Pass a file path!")

        path, fileName = os.path.split(file)

        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError as err:
            print("ERROR: Could not create directory for file")
            print(str(err))

    def checkLocalFile(self, file=None):
        """"Check whether a local file exists.

        file is a path to a local file in format: /foo/bar.txt
        """

        if file == None:
            raise ValueError("Pass a file path!")

        try:
            if os.path.exists(file):
                return True
            else:
                return False
        except OSError as err:
            print(
                "ERROR: Couldn;t read filesystem to determine file existence")
            print(str(err))

    def fetchPutIOFile(self, fileID=None, fileDir=None):
        """We will fetch a file and store it locally.

        fileID - is the file ID of the file you want to download from put.io
        fileDir - The file name and local directory to save the file.
        """

        if fileID == None or fileDir == None:
            raise ValueError('You must send a putio item id and file path.')

        if not self.contents.__contains__(fileID):
            self.getItem(fileID)

        fileName = self.contents[fileID]['name']

        print("Downloading file: " + fileName)
        resp, data = self.h.request(self.contents[fileID]['uri'])
        if resp.status >= 400:
            print("We couldn't downlaod the file: " + fileName)
            print(resp)
        else:
            with open(fileDir, 'wb') as file:
                file.write(data)

    def getItem(self, fileID=None):
        try:
            putData = self.API.get_items(id=fileID)
            for item in putData:
                self.contents[fileID] = {
                    'name': item.name, 'parentID': item.parent_id,
                    'size': item.size, 'uri': item.download_url
                }
        except putio.PutioError as err:
            print("Couldn't download file")
            print(str(err))


    def __init__(self,configLocation=None):

        #Global shit
        self.contents = {}
        if configLocation == None or not os.path.exists(configLocation):
            raise ValueError("Provide Valid Config FILE!")
            sys.exit(1)

        config = ConfigParser.RawConfigParser()
        config.read(configLocation)

        self.dlLocation = config.get('local', 'store_location') #We need to check to make sure this is /foo/bar/

        self.API = putio.Api(config.get(
            'account','api_key'), config.get('account', 'api_secret'))

        self.h = httplib2.Http('.cache')
        self.h.add_credentials(
            config.get('account', 'putio_user'),
            config.get('account', 'putio_passwd')
        )
