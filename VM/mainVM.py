#!/usr/bin/python3
# -*-coding:utf-8 -*

import time
import os,random
import utils, subprocess
from chrome import Chrome
from firefox import Firefox

nbBrowsers = 2
workingDirectory = "/media/sf_Shared/"

def randomBrowser():
    choice = random.randint(0,nbBrowsers-1)
    if choice == 0:
        return Firefox()
    else:
        return Chrome()
    
def removeJSONFile(dataPath):
    return subprocess.call("rm "+dataPath,shell=True)

def main():
    print("Browser launch script")
    
    #We remove old mozilla files to be sure to correctly
    #load plugins
    subprocess.call("find ~/.mozilla -name pluginreg.dat -type f -exec rm {} \;", shell=True)
    
    #Change the working directory to the Shared folder
    os.chdir(workingDirectory)
    
    #Look in the browser folder for the browser but 
    #Execute a different command according to the browser used
    dataPath = workingDirectory+"data.json"
    encryptedDataPath = dataPath+".gpg"   
	
    #Decrypt file if encrypted
    if os.path.isfile(encryptedDataPath):
        cancelled = False
        while not os.path.isfile(dataPath) and not cancelled:
            res = subprocess.getstatusoutput("gpg2 -d -o "+dataPath+" "+encryptedDataPath)
            if res[0] != 0 and "cancelled" in res[1]:
                cancelled = True
        subprocess.call("rm "+encryptedDataPath,shell=True)
    
    if os.path.isfile("/media/sf_Shared/chrome.browser"):
        browser = Chrome()
    else :
        browser = Firefox()

    browser.importData()
    browser.runBrowser()
    encryption = browser.exportData()

    #Encrypt file if encryption activated
    if encryption :
        done = False
        while not done :
            res = subprocess.getstatusoutput("gpg2 -c --cipher-algo=AES256 "+dataPath)
            if res[0] == 0 :
                #If the encryption went well, we removed the unencrypted file
                subprocess.call("rm "+dataPath,shell=True)
                done = True
            elif "cancelled" in res[1]:
                #If the user cancelled the encryption operation, we do nothing
                done = True

if __name__ == "__main__":
    main()



