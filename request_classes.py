#
#
#

import socket
import time
import requests
import ntplib
import dns.resolver
import dns.exception
import threading
import os
import zlib
import struct
import random
import string
from abc import ABC, abstractmethod
from typing import Tuple, Any, Optional
from time import ctime
from socket import gaierror

class RequestService(ABC):
    """the abstract class defining the behavior of concrete request classes"""
    def __init__(self):
        pass

    @abstractmethod
    def runRequest(self):
        pass


class PingService(RequestService):
    """creates an ICMP packet and pings the given server"""
    def __init__(self):
        self.packet: ICMPPacket = None

    def setICMPPacket(self, ICMPPacket):
        self.packet = ICMPPacket

    def runRequest(self, host: str, ttl: int, timeout: int, sequence_number: int) -> Tuple[Any, float] | Tuple[Any, None]:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            sock.settimeout(timeout)
            packet: bytes = self.packet.createPacket(icmp_type=8, icmp_code=0, sequence_num=sequence_number)
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
        result = [f"{'Hop':>3} {'Address':<15} {'Min (ms)':>8} {'Avg (ms)':>8} {'Max (ms)':>8} {'Count':>5}"]
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
                result.append(f"{ttl:>3} {addr[0] if addr else '*':<15} {min_ping:>8.2f}ms {avg_ping:>8.2f}ms {max_ping:>8.2f}ms {count:>5}")
            else:
                result.append(f"{ttl:>3} {'*':<15} {'*':>8} {'*':>8} {'*':>8} {0:>5}")
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
                return True, f"TCP port {port} on {ip_address} is open."
        except socket.timeout:
            return False, f"TCP port {port} on {ip_address} timed out."
        except socket.error:
            return False, f"TCP port {port} on {ip_address} is closed or unreachable."
        except Exception as exc:
            return False, f"Failed to check TCP port {port} on {ip_address} due to an error: {exc}."
        

class UdpPortService(RequestService):
    """ """
    def __init__(self):
        pass

    def runRequest(self, ip_address: str, port: int) -> Tuple[bool, Optional[str]]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(3)
                sock.sendto(b"", (ip_address, port))
                try:
                    sock.recvfrom(1024)
                    return False, f"UDP port {port} on {ip_address} is closed."
                except socket.timeout:
                    return True, f"UDP port {port} on {ip_address} is open or no response was received."
        except Exception as exc:
            return False, f"Failed to check UDP port {port} on {ip_address} due to an error: {exc}."


class ICMPPacket:
    """ """
    def __init__(self):
        pass

    def createPacket(self, icmp_type: int, icmp_code: int, sequence_num: int, data_size: int) -> bytes:
        thread_id = threading.get_ident()
        proc_id = os.getpid()
        icmp_id = zlib.crc32(f"{thread_id}{proc_id}".encode()) & 0xffff
        header: bytes = struct.pack("bbHHh", icmp_type, icmp_code, 0, icmp_id, sequence_num)
        rand_char: str = random.choice(string.ascii_letters + string.digits)
        data: bytes = (rand_char * data_size).encode()
        check_sum = self.calculateCheckSum(header + data)
        header = struct.pack("bbHHh", icmp_type, icmp_code, socket.htons(check_sum), icmp_id, sequence_num)
        return header + data
    
    def calculateCheckSum(data: bytes) -> int:
        check_sum: int = 0
        for i in range(0, len(data), 2):
            curr_num: int = (data[i] << 8) + (data[i+1])
            check_sum += curr_num
        check_sum = (check_sum >> 16) + (check_sum & 0xffff)
        check_sum = ~check_sum & 0xffff
        return check_sum
