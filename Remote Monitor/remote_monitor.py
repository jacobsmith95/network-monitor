#
#
#

from monitor_classes import RemoteClient, SocketHandler, CommsHandler, ServiceHandler


def main():
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