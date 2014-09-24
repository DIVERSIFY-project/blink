#!/usr/bin/python3
# -*-coding:utf-8 -*

import copy
import time
import random
import os
import subprocess
import dbus
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop
from threading import Thread
from os.path import expanduser

#Creation of the main loop to detect the locking of the browsing session
loop = GObject.MainLoop()

class BlinkHost(object):
    
    ##########################################################################
    allPluginsFolder = 'ALL_PLUGINS/'
    allFontsFolder = 'ALL_FONTS/'
    allBrowserFolder = 'ALL_BROWSERS/'
    allVMSFolder = "VMS/"
    sharedFolder = 'Shared/'
    confFile = sharedFolder+"conf.txt"
    sharedUserFonts = sharedFolder+'userFonts/'
    pluginsMap = {
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
      }
    ##########################################################################
    
    def __init__(self, userPlugins, plugins32List, plugins64List, browsersList, VMList):
        self.userPlugins = userPlugins
        self.plugins32List = plugins32List
        self.plugins64List = plugins64List
        self.VMList = VMList
        self.browsersList = browsersList
        self.browsersListx64 = [browser for browser in browsersList if 'x64' in browser]
        self.browsersListi386 = [browser for browser in browsersList if 'i386' in browser]

        self.currentVM = ""
        self.currentVMName = ""
        self.currentSharedFolder = BlinkHost.sharedFolder

    def start(self):

        #We randomly choose the VM
        VMName = getRandomChoice(self.VMList)
        self.currentVMName = VMName
        self.currentVM = BlinkVM(self.currentSharedFolder,self.currentVMName,self.browsersListi386,
                                 self.browsersListx64)
        self.currentVM.startVM()

        end = False

        while not end :
            if os.path.isfile(self.currentSharedFolder+"VM.shutdown"):
                #We shutdown the first VM
                self.currentVM.shutdownVM()
                #End of script
                end = True
            else :
                time.sleep(10)


######################## BLINK VM CLASS ########################
class BlinkVM(object):
    def __init__(self,sharedFolder,VMName,browsersListi386,browsersListx64):
        self.sharedFolder = sharedFolder
        self.jsonDataFile = self.sharedFolder+'data.json'
        self.sharedBrowserFolder = self.sharedFolder+'Browser/'
        self.VMName = VMName

        #We randomly choose the browser
        if '32' in self.VMName :
            browser =  getRandomChoice(browsersListi386)
        else :
            browser = getRandomChoice(browsersListx64)

        #We put a <name>.browser file to indicate the mainVM script which browser to launch
        if "chrome" in browser :
            subprocess.call("touch "+self.sharedFolder+"chrome.browser",shell=True)
        else:
            subprocess.call("touch "+self.sharedFolder+"firefox.browser",shell=True)

        #We remove the old browser and copy the new one
        subprocess.call("rm -rf "+self.sharedBrowserFolder+"*", shell=True)
        subprocess.call("cp -rf "+BlinkHost.allBrowserFolder+browser+"/* "+self.sharedBrowserFolder,shell=True)


    def startVM(self):
        #We launch the VM
        subprocess.call(["vboxmanage", "startvm", self.VMName])

    def shutdownVM(self):
        #We send a shutdown signal to the VM
        subprocess.call(["vboxmanage","controlvm",self.VMName, "acpipowerbutton"])

        #We wait for it to be shutdown
        shutdown = False
        while not shutdown:
            ret = subprocess.check_output(["vboxmanage","list","runningvms"])
            if self.VMName not in str(ret) :
                shutdown=True
            else:
                time.sleep(5)

        #We get back to the previous snapshot
        subprocess.call(["vboxmanage","snapshot",self.VMName,"restorecurrent"])

############### Coffee break
#We put in place the methods to launch a thread
#that watches the locking of the browsing session
def lockCallback(active):
    loop.quit()

def lockWatcher():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    s_bus = dbus.SessionBus()
    s_bus.add_signal_receiver(lockCallback, dbus_interface = "org.gnome.ScreenSaver", signal_name = "ActiveChanged")
    while not os.path.isfile(BlinkHost.sharedFolder+"VM.shutdown"):
        loop.run()
        subprocess.call("touch "+BlinkHost.sharedFolder+"browser.switch",shell=True)


################################################################
        
def getRandomChoice(allList):
    return allList[random.randint(0,len(allList)-1)]
        
def firstLaunch():
    #Copy the default data.json file
    subprocess.call("cp -f backupData.json Shared/data.json", shell=True)

    #We copy the user fonts into the Shared fonts directory
    userFonts = []
    fontsDirectories = ["/usr/share/fonts/","~/.fonts/".replace("~",expanduser("~"))]
    for directory in fontsDirectories :
        if os.path.isdir(directory):
            userFonts.extend([directory+font for font in os.listdir(directory)])
    for font in userFonts :
        subprocess.call(["cp","-r",font,BlinkHost.sharedUserFonts])
	
    #We scan the user plugin directories
    userPlugins = []
    pluginsDirectories = ["/usr/lib/mozilla/plugins","/opt/google/chrome/","~/.mozilla/plugins/".replace("~",expanduser("~"))]
    for directory in pluginsDirectories :
        if os.path.isdir(directory):
            userPlugins.extend(os.listdir(directory))
    userPlugins =  [plugin for plugin in userPlugins if ".so" in plugin]

    #We find which plugins of the user are in our database
    uP = copy.copy(userPlugins)
    userPlugins = []
    for plugin in uP :
        name = ""
        for key in BlinkHost.pluginsMap.keys() :
              if plugin in BlinkHost.pluginsMap[key]:
                  name = key
        if name != "":
            userPlugins.append(name)

    #We write the configuration file
    with open(BlinkHost.confFile, 'w') as dataFile:
        dataFile.write("\n".join(userPlugins))

    return userPlugins

def main():
    #We look if it is the first launch of Blink
    if os.path.isfile(BlinkHost.confFile) :
        with open(BlinkHost.confFile, 'r') as dataFile:
            lines = dataFile.readlines()
        userPlugins = [plugin.strip() for plugin in lines]
    else :
        userPlugins = firstLaunch()

    #We make a list of every elements in our database
    plugins32List = os.listdir(BlinkHost.allPluginsFolder+"32/")
    plugins64List = os.listdir(BlinkHost.allPluginsFolder+"64/")
    browsersList = os.listdir(BlinkHost.allBrowserFolder)
    VMList = os.listdir(BlinkHost.allVMSFolder)

    #We launch the lock watcher thread
    lockThread = Thread(target = lockWatcher, args = ())
    lockThread.start()
    
    #We create a BlinkHost and we launch a VM that has been synthesized in real-time
    host = BlinkHost(userPlugins, plugins32List, plugins64List, browsersList, VMList)
    host.start()

    #We quit the loop
    loop.quit()

    #We remove the temporary files
    subprocess.call("rm -f "+BlinkHost.sharedFolder+"*.browser",shell=True)
    subprocess.call("rm -f "+BlinkHost.sharedFolder+"*.shutdown",shell=True)
    subprocess.call("rm -f "+BlinkHost.sharedFolder+"*.switch",shell=True)

if __name__ == '__main__':
    main()
