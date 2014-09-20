__author__ = 'peter@phyn3t.com'

"""
This script will download everything from
"""

from fetch import fetch
import pickle
import os

get = fetch('C:/Users/pfisher/Documents/repos/putio/config.cfg')

#load our local DB of downloaded items
if os.path.exists('localdb'):
    with open('localdb', 'r') as file:
        downloadedItems = pickle.load(file)
else:
    downloadedItems = set()

try:
    #Get our Local Files
    localItems = get.getLocalFiles()

    #Get all remote put.io items
    items = get.getAllItems()

    #Iterate over all put.io items
    for item in items:

        if item in downloadedItems:
            print("We already have: " + items[item]['name'] + " locally, skipping.")
            continue

        #Figure out the local path for our put.io items
        path = get.putioPath(item)
        print(path)

        #If the file doesn't exist locally lets download it from put.io
        if not path in localItems:
            get.createLocalDirectory(path)
            get.fetchPutIOFile(item, path)
        else:
            #File on put.io already exists locally, skipping file.
            print("We already have: " + items[item]['name'] + " locally, skipping.")
            downloadedItems.add(item)

finally:
    with open('localdb', 'w') as file:
        pickle.dump(downloadedItems, file)
