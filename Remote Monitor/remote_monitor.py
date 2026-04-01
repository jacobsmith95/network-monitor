#
#
#

from monitor_classes import RemoteClient, SocketHandler, CommsHandler, ServiceHandler


def main():
    """Loads the concrete client class, the concrete handler classes, and injects the handlers into the client"""
    #console = Console()
    client = RemoteClient()
    sockethandler = SocketHandler()
    commshandler = CommsHandler()
    servicehandler = ServiceHandler()
    client.SetSocketHandler(sockethandler)
    client.SetCommsHandler(commshandler)
    client.SetServiceHandler(servicehandler)
    client.RunMonitor()

if __name__ == "__main__":
    main()