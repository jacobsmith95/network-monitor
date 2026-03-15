#
#
#

import json
import sys
import socket
import threading
from abc import ABC, abstractmethod
from rich.console import Console
from typing import Tuple
from queue import Queue


def main():
    console = Console()
    client = RemoteClient()
    sockethandler = SocketHandler()
    client.SetSocketHandler(sockethandler)
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


class AbstractHandler(ABC):
    """ """
    @abstractmethod
    def RunHandler():
        pass


class RemoteClient(AbstractClient):
    """ """
    def __init__(self):
        self.sockethandler: SocketHandler = None
        self.commshandler: CommsHandler = None
        self.servicehandler: ServiceHandler = None

        self.insocketq: Queue = Queue()
        self.outsocketq: Queue = Queue()
        self.incommsq: Queue = Queue()
        self.outcommsq: Queue = Queue()
        self.inserviceq: Queue = Queue()
        self.outserviceq: Queue = Queue()

        self.queuedict = {"in socket"  : self.insocketq,
                          "out socket" : self.outsocketq,
                          "in comms"   : self.incommsq,
                          "out comms"  : self.outcommsq,
                          "in service" : self.inserviceq,
                          "out service": self.outserviceq}

    def RunMonitor(self, ip_addr: str, port: str, console: Console) -> None:
        if not self.sockethandler:
            console.print("No sockethandler currently set, set a sockethandler to open a socket.")
            return
        if not self.commshandler:
            console.print("No commshandler currently set, set a commshandler to continue.")
            return
        if not self.servicehandler:
            console.print("No servicehandler currently set, set a servicehandler to continue.")
            return
        monitor_sock, monitor_id = self.sockethandler.RunHandler(ip_addr= ip_addr, port= port)
        console.print(f"Monitor service ID #{monitor_id} listening at {ip_addr} on port {port}.")
        comms_thread = threading.Thread(target=self.commshandler.RunHandler, args=(), daemon=True)
        console.print(f"Started CommsHandler thread for Monitor #{monitor_id}.")
        service_thread = threading.Thread(target=self.servicehandler.RunHandler, args=(), daemon=True)
        console.print(f"Started ServiceHandler thread for Monitor #{monitor_id}.")
        end_event = threading.Event()
        monitor_event = threading.Event()
        try:
            while True:
                console.print("Waiting for server connection...")
                server_socket, server_addr = monitor_sock.accept()



        finally:
            monitor_sock.close()

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
    
    def SetSocketHandler(self, sockethandler: AbstractHandler) -> None:
        self.sockethandler = sockethandler
        return

    def SetCommsHandler(self, commshandler: AbstractHandler) -> None:
        self.commshandler = commshandler
        return
    
    def SetServiceHandler(self, servicehandler: AbstractHandler) -> None:
        self.servicehandler = servicehandler
        return
    
    def ExitProgram():
        print("Exiting remote monitor...")
        sys.exit()


class SocketHandler(AbstractHandler):
    """ """
    def RunHandler(self, ip_addr: str, port: str) -> Tuple[object, str]:
        monitor_id = ip_addr + '-' + port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip_addr, int(port)))
        sock.listen(5)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        return [sock, monitor_id]

class CommsHandler(AbstractHandler):
    """ """
    def RunHandler(self, monitor_sock: socket, monitor_id: str,  queue_dict: dict, monitor_event: threading.Event) -> None:
        incommsqueue = queue_dict["in comms"]
        outcommsqueue = queue_dict["out comms"]
        while not monitor_event.is_set():
            try:
                monitor_message = monitor_sock.recv(1024)
                if monitor_message:
                    continue
                match monitor_message.decode():
                    case "check_status":
                        response = "status: on"
                        monitor_sock.sendall(response.encode())
                        continue
                    case "start_services":
                        pass
                    case "end_services":
                        pass
                    case "close_monitor":
                        pass
                    case _:
                        pass
            except socket.timeout:
                outcommsqueue.put(f"Monitor #{monitor_id} connection lost: timeout.")
                return
            except ConnectionAbortedError:
                outcommsqueue.put(f"Monitor #{monitor_id} connection lost: aborted.")
                return
            except ConnectionResetError:
                outcommsqueue.put(f"Monitor #{monitor_id} connection lost: reset.")
                return
            finally:
                continue
        return


class ServiceHandler(AbstractHandler):
    """ """
    pass


if __name__ == "__main__":
    main()