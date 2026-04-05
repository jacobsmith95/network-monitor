#
#
#

from monitor_classes import RemoteClient, SocketHandler, CommsHandler, ServiceHandler
from request_classes import PingService, TracerouteService, HttpService, HttpsService, NtpService, DnsService, TcpPortService, UdpPortService, ICMPPacket
from typing import Tuple
from rich.console import Console


def main():
    """Loads the concrete client class, the concrete handler classes, and injects the handlers into the client"""
    console = Console()

    client = RemoteClient()

    sockethandler = SocketHandler()
    commshandler = CommsHandler()
    servicehandler = ServiceHandler()
    client.SetSocketHandler(sockethandler)
    client.SetCommsHandler(commshandler)
    client.SetServiceHandler(servicehandler)

    requestservices = []
    requestservices.append(Tuple("ping", pingservice = PingService()))
    icmpservice = ICMPPacket()
    requestservices[0][1].SetICMPService(icmpservice)
    requestservices.append(Tuple("trace", tracerouteservice = TracerouteService()))
    requestservices[1][1].SetPingService(requestservices[0][1])
    requestservices.append(Tuple("http", httpservice = HttpService()))
    requestservices.append(Tuple("https", httpsservice = HttpsService()))
    requestservices.append(Tuple("ntp", ntpservice = NtpService()))
    requestservices.append(Tuple("dns", dnsservice = DnsService()))
    requestservices.append(Tuple("tcp", tcpportservice = TcpPortService()))
    requestservices.append(Tuple("udp", udpportservice = UdpPortService()))
    for service in requestservices:
        client.SetServiceEntry(service[0], service[1])

    client.RunMonitor()

if __name__ == "__main__":
    main()