__author__ = 'peter@phyn3t.com'

import putio
import os
import httplib2
import ConfigParser
import sys
import time
import re

class fetch:

    def get_items(self, parent=None, id_Number=None):
        """ Handles putio.get_items request with better error handling.

        Since the putio API will hand back HTTP exception all the time
        this function will allow them to happen without crashing your script.
        If there are no items in a directory we return an empty list.

        Return - A list of Item objects (from putio class...) or an empty list
        if there are no items to return.
        """

        sigkill = 0

        while 1:
            try:
                value = self.API.get_items(parent_id=parent, id=id_Number)
                return value
            except putio.PutioError as err:
                if str(err) == "You have no items to show.":
                    print("Empty Directory...")
                    return []
                print("Warning: Fail to make putio request. Trying again.")
                print("Debug: " + str(err))
                sigkill += 1
                if sigkill >= 3:
                    print("ERROR: Request failed too many times. Giving up!")
                    break
                time.sleep(15)
                pass


    def getAllItems(self):
        """Get entire put.io account and and save it to a dict called contents.
            This function will iterate over your entire put.io account and
            download all files. It saves the following attribuites to the
            dictionary contents: item name, parent item ID, item size, and
            download url.
         """

        control = []

        for folder in self.get_items():
            control.append(folder.id)

        while control.__len__() > 0:
            try:
                for item in self.get_items(parent=control.pop()):
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

        path = self.get_items(id_Number=itemID)[0].name

        while 1:
            itemID = self.get_items(id_Number=itemID)[0].parent_id
            if itemID == "0":
                break
            else:
                path = self.get_items(id_Number=itemID)[0].name + "/" + path

        path = path.replace('\\\\','/')
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

    def fetchPutIOFile(self, fileID=None, fileDir=None):
        """We will fetch a file and store it locally.


        fileID - is the file ID of the file you want to download from put.io
        fileDir - The file name and local directory to save the file.
        """

        sigkill = 0

        if fileID == None or fileDir == None:
            raise ValueError('You must send a putio item id and file path.')

        if not self.contents.__contains__(fileID):
            self.getItem(fileID)

        fileName = self.contents[fileID]['name']

        print("Downloading file: " + fileName)
        while 1:
            try:
                resp, data = self.h.request(self.contents[fileID]['uri'])
                if resp.status >= 400:
                    print("We couldn't downlaod the file: " + fileName)
                    print(resp)
                else:
                    with open(fileDir, 'wb') as file:
                        file.write(data)
                        break
            except httplib2.HttpLib2Error as err:
                print("Warning we had a httplib2 error... Trying again.")
                print(str(err))
                if sigkill <= 3:
                    sigkill += 1
                    pass
                else:
                    print("ERROR: We failed to fetch item 3 items. Fuck this.")

    def getItem(self, fileID=None):
        try:
            putData = self.get_items(id_Number=fileID)
            for item in putData:
                self.contents[fileID] = {
                    'name': item.name, 'parentID': item.parent_id,
                    'size': item.size, 'uri': item.download_url
                }
        except putio.PutioError as err:
            print("Couldn't download file")
            print(str(err))

    def getLocalFiles(self):
        """Gets all the files in our local putio directory

        The reason for this function is os.path.exists is so slow. Walking
        the local directory and then doing a list lookup is a lot faster. We
        also clean up the path t o make it

        ###TODO - support other drives in windows other than C.

        returns a list containing the full path of each file in our local putio
        directory.
        """

        for dirpath, dirnames, filenames in os.walk(self.dlLocation):
            for name in filenames:
                currentPath = os.path.join(dirpath, name)
                currentPath = re.sub('^\w:', '', currentPath)
                currentPath = re.sub(r"\\",'/', currentPath)
                self.localStore.append(currentPath)

        return self.localStore

    def __init__(self,configLocation=None):

        #Global shit
        self.contents = {}
        self.localStore = []

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