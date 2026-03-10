#
#
#

import socket
import time
import requests
import ntplib
import dns.resolver
import dns.exception
from typing import Tuple, Any, Optional
from time import ctime
from socket import gaierror

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


class HttpService(RequestService):
    """ """
    def __init__(self):
        pass

    def runRequest(self, url: str) -> Tuple[bool, Optional[int]]:
        try:
            response: requests.Response = requests.get(url)
            up_status: bool = response.status_code < 400
            return up_status, response.status_code
        except requests.RequestException:
            return False, None
        

class HttpsService(RequestService):
    """ """
    def __init__(self):
        pass

    def runRequest(self, url: str, timeout: int) -> Tuple[bool, Optional[int], str]:
        try:
            headers: dict = {'User-Agent':'Mozilla/5.0'}
            response: requests.Response = requests.get(url, headers=headers, timeout=timeout)
            up_status: bool = response.status_code < 400
            return up_status, response.status_code, "Server is up."
        except requests.ConnectionError:
            return False, None, "Connection Error."
        except requests.Timeout:
            return False, None, "Connection Timeout."
        except requests.RequestException as exc:
            return False, None, f"Error during request: {exc}."
        

class NtpService(RequestService):
    """ """
    def __init__(self):
        pass

    def runRequest(self, server: str) -> Tuple[bool, Optional[str]]:
        client = ntplib.NTPClient()
        try:
            response = client.request(server, version=3)
            return True, ctime(response.tx_time)
        except (ntplib.NTPException, gaierror):
            return False, None
        

class DnsService(RequestService):
    """ """
    def __init__(self):
        pass

    def runRequest(self, server: str, query: str, record_type: str) -> Tuple[bool, Optional[str]]:
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [socket.gethostbyname(server)]
            query_result = resolver.resolve(query, record_type)
            result = [str(rdata) for rdata in query_result]
            return True, result
        except (dns.exception.Timeout, dns.resolver.NoNameservers, dns.resolver.NoAnswer, gaierror) as exc:
            return False, f"Error during request: {exc}."
        

class TcpPortService(RequestService):
    """ """
    def __init__(self):
        pass

    def runRequest(self, ip_address: str, port: int) -> Tuple[bool, Optional[str]]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                sock.connect((ip_address, port))
                return True, f"Port {port} on {ip_address} is open."
        except socket.timeout:
            return False, f"Port {port} on {ip_address} timed out."
        except socket.error:
            return False, f"Port {port} on {ip_address} is closed or unreachable."
        except Exception as exc:
            return False, f"Failed to check port {port} on {ip_address} due to an error: {exc}."
        


