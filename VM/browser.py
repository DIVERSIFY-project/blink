#!/usr/bin/python3
# -*-coding:utf-8 -*

from abc import ABCMeta, abstractmethod
import utils

class Browser(object):
    __metaclass__ = ABCMeta
    
    #ENUMS
    #actions
    #browsers
    
    #METHODS
    def __init__(self):
        self.dataPath = utils.relativeToAbsoluteHomePath("/media/sf_Shared/data.json")
    
    @abstractmethod
    def importData(self):
        raise NotImplementedError("importData function not implemented")

    @abstractmethod
    def exportData(self):
        raise NotImplementedError("exportData function not implemented")
    
    @abstractmethod
    def runBrowser(self):
        raise NotImplementedError("runBrowser function not implemented")
    

