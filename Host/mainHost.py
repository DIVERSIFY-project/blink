#!/usr/bin/python3
# -*-coding:utf-8 -*
import copy
import json
import uuid
import time
import numpy
import random
import os,re,sys
import subprocess
from os.path import expanduser

class BlinkHost(object):
    
    ##########################################################################
    allPluginsFolder = 'ALL_PLUGINS/'
    allFontsFolder = 'ALL_FONTS/'
    allBrowserFolder = 'ALL_BROWSERS/'
    allVMSFolder = "VMS/"
    confFile = "conf.txt"
    sharedFolder = 'Shared/'
    jsonDataFile = sharedFolder+'data.json'
    sharedFontsFolder = sharedFolder+'Fonts/'
    sharedPluginsFolder = sharedFolder+'Plugins/'
    sharedBrowserFolder = sharedFolder+'Browser/'
    averageNbFonts = 261.0094
    sdFonts = 91.45935
    ##########################################################################
    
    def __init__(self, userPlugins, plugins32List, plugins64List, fontsList, browsersList, VMList):
        self.userPlugins = userPlugins
        self.plugins32List = plugins32List
        self.plugins64List = plugins64List
        self.fontsList = fontsList
        self.VMList = VMList
        self.browsersList = browsersList
        self.browsersListx64 = [browser for browser in browsersList if 'x64' in browser]
        self.browsersListi386 = [browser for browser in browsersList if 'i386' in browser]
        self.jsonDataFile = BlinkHost.jsonDataFile
        self.pluginsMap = {
                  'Shockwave Flash' : ['libflashplayer.so','libgnashplugin.so','liblightsparkplugin.so','libtotem-vegas-plugin.so'],
                  'GnomeShellIntegration' : ['libgnome-shell-browser-plugin.so'],
                  'iTunesApplicationDetector' : ['librhythmbox-itms-detection-plugin.so'],
                  'VLC Multimedia Plugin' : ['libtotem-cone-plugin.so','libvlcplugin-gtk.so'],
                  'VLC Web Plugin' : ['libvlcplugin-generic.so'],
                  'Windows Media Player Plug-in' : ['libtotem-gmp-plugin.so','gecko-mediaplayer-wmp.so'],
                  'DivX® Web Player' : ['libtotem-mully-plugin.so'],
                  'DivX Browser Plug-In' : ['gecko-mediaplayer-dvx.so'],
                  'QuickTime Plug-in' : ['libtotem-narrowspace-plugin.so'],
                  'LibreOffice Plug-in' : ['libnpsoplugin.so'],
                  'Google Talk Plugin Video Renderer' : ['libnpo1d.so'],
                  'Google Talk Plugin' : ['libnpgoogletalk.so'],
                  'Xine Plugin' : ['xineplugin.so'],
                  'gxine starter plugin' : ['gxineplugin.so'],
                  'DjView' : ['nsdejavu.so'],
                  'Estonian ID card plugin' : ['npesteid.so'],
                  'FreeWRL X3D/VRML' : ['libFreeWRLplugin.so'],
                  'KParts Plugin' : ['libkpartsplugin.so'],
                  'MozPlugger' : ['mozplugger.so'],
                  'NPAPI Plugins Wrapper' : ['npwrapper.so'],
                  'PackageKit' : ['packagekit-plugin.so'],
                  'RealPlayer' : ['gecko-mediaplayer-rm.so'],
                  'Skype Buttons' : ['skypebuttons.so'],
                  'Spice Firefox Plugin' : ['npSpiceConsole.so'],
                  'X2GoClient Plug-in' : ['libx2goplugin.so'],
                  'mplayerplug-in' : ['gecko-mediaplayer.so'],
                  'Java' : ['IcedTeaPlugin.so','libjava6.so','libjava7.so','libjava8.so']
                  #'Chrome PDF Viewer' : 'libpdf.so'
                  #'Native Client' : 'libppGoogleNaClPluginChrome.so'
                  #'Widevine Content Decryption Module' : 'libwidevinecdmadapter.so'
                  }
    
    def startVM(self):
        #We find which plugins of the user are in our database
        uP = copy.copy(self.userPlugins)
        self.userPlugins = []
        for plugin in uP :
            name = ""
            for key in self.pluginsMap.keys() :
                  if plugin in self.pluginsMap[key]:
                      name = key
            if name != "":
                self.userPlugins.append(name)
        
        #We randomly choose the VM
        VMName = getRandomChoice(self.VMList)
        
        #We randomly choose the browser
        #We randomly choose the plugins
        if '32' in VMName :
            browser =  getRandomChoice(self.browsersListi386)
            finalPluginsFolder = BlinkHost.allPluginsFolder+"32/" 
            finalPluginsList = getRandomChoiceList(self.plugins32List,self.userPlugins)
        else :
            browser = getRandomChoice(self.browsersListx64)
            finalPluginsFolder = BlinkHost.allPluginsFolder+"64/"
            finalPluginsList = getRandomChoiceList(self.plugins64List,self.userPlugins)

        #We put a <name>.browser file to indicate the mainVM script
        #which browser to launch
        if "chrome" in browser :
            subprocess.call("touch Shared/chrome.browser",shell=True)
        else:
            subprocess.call("touch Shared/firefox.browser",shell=True)
                 
        #We randomly choose the fonts
        randomNbFonts = int(numpy.random.normal(loc=BlinkHost.averageNbFonts,scale=BlinkHost.sdFonts))
        finalFontsList = random.sample(self.fontsList,randomNbFonts)
        
        #We remove the old browser and copy the new one
        subprocess.call("rm -rf "+BlinkHost.sharedBrowserFolder+"*", shell=True)
        subprocess.call("cp -rf "+BlinkHost.allBrowserFolder+browser+"/* "+BlinkHost.sharedBrowserFolder,shell=True)
                        
        #We remove the old fonts and copy the new ones
        subprocess.call("rm -rf Shared/Fonts/*",shell=True)
        for font in finalFontsList:
            subprocess.call(["cp","-rf",font,BlinkHost.sharedFontsFolder])
        
        #We remove the old plugins and copy the new ones
        subprocess.call("rm -rf Shared/Plugins/*",shell=True)
        for plugin in finalPluginsList:
            subprocess.call(["cp",finalPluginsFolder+plugin,BlinkHost.sharedPluginsFolder])
        
        #We launch the VM
        subprocess.call(["vboxmanage", "startvm", VMName])
        
        #We wait for it to be shutdown
        shutdown = False
        while not shutdown:
            ret = subprocess.check_output(["vboxmanage","list","runningvms"])
            if len(ret) == 0:
                shutdown=True
            else:
                time.sleep(10)
                
        #We get back to the previous snapshot
        subprocess.call(["vboxmanage","snapshot",VMName,"restorecurrent"])

        #We remove the .browser file
        subprocess.call("rm Shared/*.browser",shell=True)
        
def getRandomChoiceList(*args):
    if len(args) == 1:
        allList = args[0]
        return random.sample(allList,random.randint(0,len(allList)))
    else :
        allList = args[0]
        requiredList = args[1]
        randomList = [file for file in allList if file not in requiredList]
        finalList = list(requiredList)
        sample_size = random.randint(0,len(randomList))
        finalList.extend(random.sample(randomList,sample_size))
        return finalList

def getRandomChoice(allList):
    return allList[random.randint(0,len(allList)-1)]
        
def firstLaunch():
    #Copy the default data.json file
    subprocess.call("cp -f backupData.json Shared/data.json", shell=True)

    #We scan the user plugin directories
    userPlugins = []
    pluginsDirectories = ["/usr/lib/mozilla/plugins","/opt/google/chrome/","~/.mozilla/plugins/".replace("~",expanduser("~"))]
    for directory in pluginsDirectories :
        userPlugins.extend(os.listdir(directory))
    userPlugins =  [plugin for plugin in userPlugins if ".so" in plugin]
    with open(BlinkHost.confFile, 'w') as dataFile:
        dataFile.write("\n".join(userPlugins))
    return userPlugins

def main():   
	#We look if it is the first launch of Blink
    if os.path.isfile(BlinkHost.confFile) :
        with open(BlinkHost.confFile, 'r') as dataFile:
            userPlugins = dataFile.readlines()
        userPlugins = [plugin.strip() for plugin in userPlugins]
    else :
        userPlugins = firstLaunch()

	#We make a list of every elements in our database
    plugins32List = os.listdir(BlinkHost.allPluginsFolder+"32/")
    plugins64List = os.listdir(BlinkHost.allPluginsFolder+"64/")
    fontsList = []
    for root, dirs, files in os.walk(BlinkHost.allFontsFolder): 
        for file in files: 
            fontsList.append(os.path.abspath(os.path.join(root, file))) 
    browsersList = os.listdir(BlinkHost.allBrowserFolder)
    VMList = os.listdir(BlinkHost.allVMSFolder)
    
    #We create a BlinkHost and we launch a VM that has been synthesized in real-time
    host = BlinkHost(userPlugins, plugins32List, plugins64List, fontsList, browsersList, VMList)
    host.startVM()

if __name__ == '__main__':
    main()
