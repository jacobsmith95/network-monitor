#
#
#

import json
import sys
import socket
import threading
from abstract_classes import AbstractClient, AbstractHandler, AbstractRequest
from rich.console import Console
from typing import Tuple
from queue import Queue


class RemoteClient(AbstractClient):
    """The concrete remote client class which runs the general monitor, reads and writes settings, and does handler injection and thread creation"""
    def __init__(self):
        self.sockethandler: SocketHandler = None
        self.commshandler: CommsHandler = None
        self.servicehandler: ServiceHandler = None

        self.servicedict: dict = {}

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
                console.print(f"Connection from {server_addr} for Monitor #{monitor_id}.")
                console.print(f"Starting CommsHandler and ServiceHandler threads for Monitor #{monitor_id}")
                comms_thread.start()
                service_thread.start()
                message = self.outsocketq.get()
                if message:
                    console.print(f"Monitor Message: {message}.")
                    console.print(f"Ending Client Thread at {server_addr} for Monitor #{monitor_id}.")
                    monitor_event.set()
                    comms_thread.join()
                    service_thread.join()
                    monitor_event.clear()
                    server_socket.shutdown(1)
                    server_socket.close()
                    console.print(f"Server Socket closed at {server_addr} for Monitor #{monitor_id}.")
                    monitor_event.clear()
                continue
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
    
    def SetServiceEntry(self, key: str, servicerequest: AbstractRequest) -> None:
        self.servicedict.update({key: servicerequest})
        return
    
    def ExitProgram():
        print("Exiting remote monitor...")
        sys.exit()


class SocketHandler(AbstractHandler):
    """Concrete class for creating and listening to a socket in order to communicate with the managing server over TCP"""
    def RunHandler(self, ip_addr: str, port: str) -> Tuple[object, str]:
        monitor_id = ip_addr + '-' + port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip_addr, int(port)))
        sock.listen(5)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        return [sock, monitor_id]

class CommsHandler(AbstractHandler):
    """Concrete class for handling communications from the server and coordinating communication between the manager threads"""
    def RunHandler(self, server_sock: socket, monitor_id: str,  queue_dict: dict, monitor_event: threading.Event) -> None:
        incommsqueue = queue_dict["in comms"]
        outcommsqueue = queue_dict["out comms"]
        while not monitor_event.is_set():
            try:
                server_message = server_sock.recv(1024)
                if server_message:
                    continue
                match server_message.decode():
                    case "check_status":
                        response = "status: on"
                        server_sock.sendall(response.encode())
                        continue
                    case "start_services":
                        pass
                    case "end_services":
                        pass
                    case "close_comms":
                        response = "connection closed"
                        server_sock.sendall(response.encode())
                        continue
                    case _:
                        config = json.loads(server_message.decode())
                        response = "updated config"
                        server_sock.sendall(response.encode())
                        continue
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
    """Concrete class for ServiceHandler, which creates service threads based on server communication"""
    def __init__(self, monitor_config: dict):
        self.config: dict = monitor_config
        self.threads: set = set()

    def RunHandler(self) -> None:
        for key1 in self.config:
            for key2 in self.config[key1]:
                thread_name = "thread_" + str(key2) + "_" + str(key1)
                match key2:
                    case "http":
                        pass
                    case "https":
                        pass
                    case "icmp":
                        pass
                    case "dns":
                        pass
                    case "ntp":
                        pass
                    case "tcp":
                        pass
                    case "udp":
                        pass
        while True:
            message = "0"
            match message:
                case "end":
                    end_event.set()
                    for thread in self.threads:
                        thread.join()
                    end_event.clear()
                    return
                case _:
                    pass
