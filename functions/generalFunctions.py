import os
import sys

# Adapted from https://stackoverflow.com/questions/17576366/print-out-the-whole-directory-tree
def getDirectoryStructure(rootDir) -> dict:
    ''' Get the directory structure of a given directory.
    Returns a nested dictionary of all folders and a list files within each folder, within a given directory.
    Ignores hidden files and folders (starting with a .) '''
    items = {}
    # First, get all folders and create their nested dictionaries
    for item in os.listdir(rootDir):
        filePath = os.path.join(rootDir, item) 
        #print(item)

        if item[0] != '.':
            if os.path.isdir(filePath):
                items[item] = getDirectoryStructure(filePath) # Recursively get the directory structure of the folder

    # Then, get all files and add them to the 'files' key of the folder dictionary
    items['files'] = []
    for item in os.listdir(rootDir):
        filePath = os.path.join(rootDir, item)

        if item[0] != '.':
            if os.path.isfile(filePath):
                items['files'].append(item)

    return items

def resourcePath(relativePath):
    ''' Replace the relative path with the absolute path to the resource. This allows files to be accessed when the program is compiled. '''
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)