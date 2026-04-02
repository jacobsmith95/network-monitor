#
#
#

from monitor_classes import RemoteClient, SocketHandler, CommsHandler, ServiceHandler
from request_classes import PingService, TracerouteService, HttpService, HttpsService, NtpService, DnsService, TcpPortService, UdpPortService
from typing import Tuple


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

    requestservices = []
    requestservices.append(pingservice = PingService())
    requestservices.append(tracerouteservice = TracerouteService())
    requestservices.append(httpservice = HttpService())
    requestservices.append(httpsservice = HttpsService())
    requestservices.append(ntpservice = NtpService())
    requestservices.append(dnsservice = DnsService())
    requestservices.append(tcpportservice = TcpPortService())
    requestservices.append(udpportservice = UdpPortService())



    client.RunMonitor()

if __name__ == "__main__":
    main()