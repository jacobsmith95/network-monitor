#This file contains all of the abstract classes for the remote monitor.
#Each class is a contract that the concrete classes must fulfill, delineating __init__ requirements and necessary methods.

from abc import ABC, abstractmethod


class AbstractRequest(ABC):
    """the abstract request class defining the behavior of concrete request classes"""
    def __init__(self):
        pass

    @abstractmethod
    def NetRequest(self):
        pass

    @abstractmethod
    def RunRequest(self):
        pass


class AbstractClient(ABC):
    """the abstract client class defining the behavior of concrete client classes"""
    @abstractmethod
    def RunMonitor():
        pass

    @abstractmethod
    def ReadSettings():
        pass

    @abstractmethod
    def WriteSettings():
        pass

    @abstractmethod
    def SetSocketHandler():
        pass

    @abstractmethod
    def SetServiceHandler():
        pass

    @abstractmethod
    def SetCommsHandler():
        pass

    @abstractmethod
    def ExitProgram():
        pass


class AbstractHandler(ABC):
    """the abstract handler class defining the behavior of concrete handler classes"""
    @abstractmethod
    def RunHandler():
        pass