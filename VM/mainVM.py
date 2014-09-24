#!/usr/bin/python3
# -*-coding:utf-8 -*

import time
import os
import random
import utils
import subprocess
import numpy
from chrome import Chrome
from firefox import Firefox

############### VM Class
class VM(object):

	### Environment variables
	nbBrowsers = 2
	blinkFolder = '/home/blink/blink/'
	allPluginsFolder = blinkFolder+'plugins/'
	allFontsFolder = blinkFolder+'fonts/'

	sharedFolder = '/media/sf_Shared/'
	jsonDataFile = sharedFolder+'data.json'

	destFontsFolder = '/home/blink/.fonts/'
	destPluginsFolder = '/home/blink/.mozilla/plugins/'

	averageNbFonts = 261.0094
	sdFonts = 91.45935
	averageNbPlugins = 12.6303
	sdPlugins = 5.7451

	### Init
	def __init__(self):
		#We read the user configuration file
		with open(VM.sharedFolder+'conf.txt', 'r') as dataFile:
			lines = dataFile.readlines()
		self.userPlugins = [plugin.strip() for plugin in lines]

		#List of plugins
		self.pluginsList = []
		for root, dirs, files in os.walk(VM.allPluginsFolder):
			for file in files:
				self.pluginsList.append(os.path.abspath(os.path.join(root, file)))

		#List of fonts
		self.fontsList = []
		for root, dirs, files in os.walk(VM.allFontsFolder):
			for file in files:
				self.fontsList.append(os.path.abspath(os.path.join(root, file)))

		#JSON data file
		self.jsonDataFile = VM.jsonDataFile

	### PLUGINS
	def selectPlugins(self):
		nbRandomPlugins = int(numpy.random.normal(loc=VM.averageNbPlugins,scale=VM.sdPlugins))
		while nbRandomPlugins < 1 :
			nbRandomPlugins = int(numpy.random.normal(loc=VM.averageNbPlugins,scale=VM.sdPlugins))

		randomPluginsList = [file for file in self.pluginsList if file not in self.userPlugins]
		finalPluginsList = list(self.userPlugins)
		if nbRandomPlugins > len(randomPluginsList):
			finalPluginsList = list(self.pluginsList)
		else :
			finalPluginsList.extend(random.sample(randomPluginsList,nbRandomPlugins))

		#We remove old mozilla files to be sure to correctly load plugins
		subprocess.call("find ~/.mozilla -name pluginreg.dat -type f -exec rm {} \;", shell=True)

		#We remove the old plugins and copy the new ones
		subprocess.call("rm -rf "+VM.destPluginsFolder+"*",shell=True)
		for plugin in finalPluginsList:
			subprocess.call(["cp",plugin,VM.destPluginsFolder])

	### FONTS
	def selectFonts(self):
		nbRandomFonts = int(numpy.random.normal(loc=VM.averageNbFonts,scale=VM.sdFonts))
		while nbRandomFonts < 1:
			nbRandomFonts = int(numpy.random.normal(loc=VM.averageNbFonts,scale=VM.sdFonts))
		finalFontsList = random.sample(self.fontsList,nbRandomFonts)

		#We remove the old fonts, recreate the link to the user fonts and copy the new ones
		subprocess.call("rm -rf "+VM.destFontsFolder+"*",shell=True)
		subprocess.call("ln -s /media/sf_Shared/userFonts/ ~/.fonts/sf_UserFonts",shell=True)
		for font in finalFontsList:
			subprocess.call(["cp",font,VM.destFontsFolder])


############### Main
def main():
	print("Blink VM Main script")

	#Change the working directory to the Shared folder
	os.chdir(VM.sharedFolder)

	#We create an instance of a VM
	machine = VM()

	#We chose the fonts and the plugins
	machine.selectFonts()
	machine.selectPlugins()

	#We look for the JSON data file
	dataPath = VM.jsonDataFile
	encryptedDataPath = dataPath+".gpg"

	#Decrypt file if encrypted
	if os.path.isfile(encryptedDataPath):
		cancelled = False
		while not os.path.isfile(dataPath) and not cancelled:
			res = subprocess.getstatusoutput("gpg2 -d -o "+dataPath+" "+encryptedDataPath)
			if res[0] != 0 and "cancelled" in res[1]:
				cancelled = True
		subprocess.call("rm "+encryptedDataPath,shell=True)

	#Look in the browser folder for the browser but
	#Execute a different command according to the browser used
	if os.path.isfile(VM.sharedFolder+"chrome.browser"):
		browser = Chrome()
	else :
		browser = Firefox()

	#We import the user profile inside the browser
	browser.importData()

	#We initialise a boolean to indicate if the
	#VM must be shutdown
	shutdown = False

	while not shutdown :
		#We launch the browser
		browserProcess = browser.runBrowser()

		#We wait for either the browsing session to be finished or the computer to be locked
		while not isinstance(browserProcess.poll(),int) and not os.path.isfile(VM.sharedFolder+"browser.switch"):
			time.sleep(10)

		encryption = browser.exportData()

		#If the browsing session is finished
		if isinstance(browserProcess.poll(),int) :
			#Encrypt file if the encryption is activated
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

			#We write a file to signal the host to shutdown all running VMs
			subprocess.call("touch "+VM.sharedFolder+"VM.shutdown", shell=True)

			#We finish the execution of the script
			shutdown = True

		else :
			#We terminate the browser process
			browserProcess.kill()

			#We switch the list of plugins and fonts
			machine.selectFonts()
			machine.selectPlugins()

			#We remove the "browser.switch" file
			subprocess.call("rm "+VM.sharedFolder+"browser.switch",shell=True)


if __name__ == "__main__":
	main()