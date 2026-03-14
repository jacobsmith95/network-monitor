#
#
#

import json
import sys
import socket
from abc import ABC, abstractmethod
from rich.console import Console
from typing import Tuple


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
    @abstractmethod
    def CreateSocket():
        pass


class AbstractCommsHandler(ABC):
    """ """
    pass


class AbstractServiceHandler(ABC):
    """ """
    pass


class RemoteClient(AbstractClient):
    """ """
    def __init__(self):
        self.sockethandler = None

    def RunMonitor() -> None:
        console = Console()
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
    
    def SetSocketHandler(self, sockethandler):
        self.sockethandler = sockethandler
    
    def ExitProgram():
        print("Exiting remote monitor...")
        sys.exit()


class SocketHandler(AbstractSocketHandler):
    """ """
    def CreateSocket(self, ip_addr: str, port: str) -> Tuple[object, str]:
        monitor_id = ip_addr + '-' + port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip_addr, int(port)))
        sock.listen(5)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        return [sock, monitor_id]

class CommsHandler(AbstractCommsHandler):
    """ """
    pass


class ServiceHandler(AbstractServiceHandler):
    """ """
    pass


if __name__ == "__main__":
    main()