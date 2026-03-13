#
#
#

import json
import sys
from abc import ABC, abstractmethod

def main():
    client = RemoteClient()
    client.RunMonitor()


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


class AbstractSocketHandler(ABC):
    """ """
    pass


class AbstractCommsHandler(ABC):
    """ """
    pass


class AbstractServiceHandler(ABC):
    """ """
    pass


class RemoteClient(AbstractClient):
    """ """
    def RunMonitor() -> None:
        pass

    def ReadSettings(monitor_id: str) -> str:
        with open(f"monitor_config_{monitor_id}.txt", "r") as file:
            config = json.load(file)
        file.close()
        return config
    
    def WriteSettings(monitor_id: str, config: str) -> None:
        with open(f"monitor_config_{monitor_id}.txt", "w") as file:
            json.dump(config, file)
        file.close()
        return
    
    def ExitProgram():
        print("Exiting remote monitor...")
        sys.exit()


class SocketHandler(AbstractSocketHandler):
    """ """
    pass

class CommsHandler(AbstractCommsHandler):
    """ """
    pass


class ServiceHandler(AbstractServiceHandler):
    """ """
    pass


if __name__ == "__main__":
    main()