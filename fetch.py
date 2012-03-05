__author__ = 'peter@phyn3t.com'

import putio
import os
import httplib2
import ConfigParser
import sys

class fetch:

    def getAllItems(self):
        """Get entire put.io account and return a dict

         """

        self.contents = {}
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

        print(self.contents) #DEBUG


    def putioPath(self, itemID=None):
        """Figures out the full path to fill on Put.io

        id equals the id of the file which you want to determine the path for
        returns a string that contains the path of the file /foo/bar.txt
        """

        path = self.API.get_items(id=itemID)[0].name

        while (True):
            itemID = self.API.get_items(id=itemID)[0].parent_id
            if itemID == "0":
                break
            else:
                path = self.API.get_items(id=itemID)[0].name + "/" + path
        return  "/" + path

    def CreateLocalDirectory(self, file=None):
        """Check whether local file and directory tree exists. Create if not.

        file is a path to a local file. In format: /foo/bar.txt if it doesn't
        exist we will create both the file and the directories to the file
        location as it is found on put.io

        Return False if file doesn't exist and True if the file exist.
        """
        if file == None:
            raise ValueError("Pass a file path!")

        path = os.split(file)

        try:
            if not os.path.exists(path):
                os.makedirs(path)
                return False
            elif os.path.exists(file):
                return True
            else:
                return False
        except OSError as err:
            print("ERROR: Could not create directory for file")
            print(str(err))

    def fetchPutIOFile(self, fileID=None, fileDir=None):
        """We will fetch a file and store it locally.

        fileID - is the file ID of the file you want to download from put.io
        fileDir - The file name and local directory to save the file.
        """

        with open(fileDir, 'wb') as file:
            data = self.h.request.urlopen(self.contents[fileID]['uri']).read()
            file.write(data)



    def __init__(self,configLocation=None):

        if configLocation == None: #Check to make sure config exists
            raise ValueError("Provide Valid Config FILE!")
            sys.exit(1)

        config = ConfigParser.RawConfigParser()
        config.read(configLocation)

        self.API = putio.Api(config.get(
            'account','api_key'), config.get('account', 'api_secret'))

        self.h = httplib2.Http('.cache')
        self.h.add_credentials(
            config.get('account', 'putio_user'),
            config.get('account', 'putio_psswd')
        )

        self.getAllItems()
        self.fetchPutIOFile(
            '28855313', 'C:/Users/pfisher/Desktop/front.png')#DEBUG REMOVE




cat = fetch('config.cfg')