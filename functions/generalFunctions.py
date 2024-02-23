''' General functions that are used throughout the program. '''
import os
import sys
import platform
import subprocess
import shutil

if platform.system() == "Windows": # If the system is Windows, get the desktop directory from the USERPROFILE environment variable
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') # Get the desktop directory
else: # If the system is not Windows (MacOS or Linux), get the desktop directory from the home directory
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

# Adapted from https://stackoverflow.com/questions/17576366/print-out-the-whole-directory-tree
def getDirectoryStructure(rootDir) -> dict:
    ''' Recursively get the directory structure of a given directory.
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
    ''' Replace the relative path with the absolute path to the resource. This allows files to be accessed when the program is compiled to an executable. '''
    try:
        basePath = sys._MEIPASS # PyInstaller creates a temp folder and stores path in _MEIPASS
    except Exception: # If not running as a PyInstaller executable, use the current directory
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath) # Return the absolute path to the resource

def showFileExplorer(file):
    ''' Function to open the file explorer to the file. '''
    filePath = resourcePath(file)
    if platform.system() == "Windows":
        os.startfile(filePath)
    elif platform.system() == "Darwin":
        subprocess.call(["open", "-R", filePath])
    else:
        subprocess.Popen(["xdg-open", filePath])

def copyFile(file):
    ''' Function to copy the file to the destination. In this case, the desktop. '''
    filePath = resourcePath(file)
    # destinationPath = resourcePath(destination)
    shutil.copy2(filePath, desktop)