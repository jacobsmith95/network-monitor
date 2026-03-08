#
#
#

import socket
import time
from typing import Tuple, Any

class RequestService():
    """the abstract class defining the behavior of concrete request classes"""
    def __init__(self):
        pass

    def runRequest(self):
        pass


class PingService(RequestService):
    """creates an ICMP packet and pings the given server"""
    def __init__(self):
        pass

    def runRequest(self, host: str, ttl: int, timeout: int, sequence_number: int) -> Tuple[Any, float] | Tuple[Any, None]:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            sock.settimeout(timeout)
            packet: bytes = ""
            sock.sendto(packet, (host, 1))
            start: float = time.time()
            try:
                data, addr = sock.recvfrom(1024)
                end: float = time.time()
                total_time = (end-start)*1000
                return addr, total_time
            except socket.timeout:
                return None, None
            

class TracerouteService(RequestService):
    """ """
    def __init__(self):
        self.ping: PingService = None


    def setPingRequest(self, PingService):
        self.ping = PingService

    def runRequest(self, host: str, max_hops: int, pings_per_hop: int, verbose: bool) -> str:
        result = [f"{'Hop'} {'Address'} {'Min (ms)'} {'Avg (ms)'} {'Max (ms)'} {'Count'}"]
        for ttl in range(1, max_hops+1):
            if verbose:
                print(f"Pinging {host} with ttl: {ttl}")
            ping_times = []
            for number in range(pings_per_hop):
                addr, response = self.ping.runRequest()
                if response is not None:
                    ping_times.append(response)
            if ping_times:
                min_ping = min(ping_times)
                avg_ping = sum(ping_times)/len(ping_times)
                max_ping = max(ping_times)
                count = len(ping_times)
                result.append(f"")
            else:
                result.append(f"")
            if verbose and result:
                print(f"\tResult: {result[-1]}")
            if addr and addr[0] == host:
                break
        return "\n".join(result)
