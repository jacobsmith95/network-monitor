#
#
#

from abc import ABC, abstractmethod


class AbstractRequest(ABC):
    """the abstract class defining the behavior of concrete request classes"""
    def __init__(self):
        pass

    @abstractmethod
    def RunRequest(self):
        pass

    @abstractmethod
    def NetRequest(self):
        pass


class AbstractClient(ABC):
    """ """
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
    """ """
    @abstractmethod
    def RunHandler():
        pass