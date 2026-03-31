#
#
#

from monitor_classes import RemoteClient, SocketHandler, CommsHandler, ServiceHandler


def main():
    #console = Console()
    client = RemoteClient()
    sockethandler = SocketHandler()
    client.SetSocketHandler(sockethandler)
    client.RunMonitor()