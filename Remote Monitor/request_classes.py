#This is the file containing the classes for network requests.
#Each network request class contains at least 2 methods: NetRequest and RunRequest.
#NetRequest is the method that contains the network check logic for each protocol type.
#RunRequest contains the logic for checking the threading end_event and running the NetRequest method once each given interval.

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
from abstract_classes import AbstractRequest
from typing import Tuple, Any, Optional
from time import ctime
from socket import gaierror
from queue import Queue


class PingService(AbstractRequest):
    """The class governing methods to ping a given address and perform the periodic network ping check."""
    def __init__(self):
        """Initializes the PingService instance with an unset icmpservice."""
        self.icmpservice: ICMPPacket = None

    def SetICMPService(self, ICMPservice: ICMPPacket):
        """Injects an ICMP service for PingService to use."""
        self.icmpservice = ICMPservice

    def NetRequest(self, host: str, ttl: int, timeout: int, sequence_number: int) -> Tuple[Any, float] | Tuple[Any, None]:
        """Runs a ping request, requiring a host, time to live, timeout value, and a sequence number; returns a tuple with the address and response time."""
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            sock.settimeout(timeout)
            packet: bytes = self.packet.CreatePacket(icmp_type=8, icmp_code=0, sequence_num=sequence_number)
            sock.sendto(packet, (host, 1))
            start: float = time.time()
            try:
                data, addr = sock.recvfrom(1024)
                end: float = time.time()
                total_time = (end-start)*1000
                return addr, total_time
            except socket.timeout:
                return None, None
            
    def RunRequest(self, monitor_id: str, url: str, args: Tuple, out_queue: Queue, end_event: threading.Event):
        """Deconstructs an arg tuple into the needed variables, and runs a NetRequest each time interval."""
        ttl, timeout, interval = args[0], args[1], args[2]
        while not end_event.is_set():
            data = self.NetRequest(url, ttl, timeout)
            print_time = time.asctime(time.localtime())
            out_queue.put(f"{print_time} | ID: {monitor_id} | icmp | ping | {url} | Address: {data[0]} | Response Time (ms): {data[1]}")
            time.sleep(interval)


class TracerouteService(AbstractRequest):
    """The class governing the methods to traceroute a given address and perform the periodic traceroute check."""
    def __init__(self):
        """Initializes a TracerouteService instance with an unset PingService."""
        self.ping: PingService = None

    def SetPingService(self, PingService):
        """Sets a PingService for the TracerouteService to use."""
        self.ping = PingService

    def NetRequest(self, host: str, max_hops: int, pings_per_hop: int, verbose: bool) -> str:
        """Performs a bespoke traceroute request on the given address, requires a host, max_hops, pings_per_hop, and verbose; returns a string with the traceroute information for each hop."""
        result = [f"{'Hop':>3} {'Address':<15} {'Min (ms)':>8} {'Avg (ms)':>8} {'Max (ms)':>8} {'Count':>5}"]
        for ttl in range(1, max_hops+1):
            if verbose:
                print(f"Pinging {host} with ttl: {ttl}")
            ping_times = []
            for number in range(pings_per_hop):
                addr, response = self.ping.RunRequest()
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
    
    def RunRequest(self, monitor_id: str, url: str, args: Tuple, out_queue: Queue, end_event: threading.Event):
        """Deconstructs the arg tuple and runs a NetRequest each given time interval."""
        max_hops, pings_per_hop, verbose, interval = args[0], args[1], args[2], args[3]
        while not end_event.is_set():
            data = self.NetRequest(url, max_hops, pings_per_hop, verbose)
            print_time = time.asctime(time.localtime())
            out_queue.put(f"{print_time} | ID: {monitor_id} | icmp | traceroute | {url} | Route: {data}")
            time.sleep(interval)


class HttpService(AbstractRequest):
    """The class governing methods to perform an HTTP check on a given address and perform the periodic HTTP check."""
    def __init__(self):
        pass

    def NetRequest(self, url: str) -> Tuple[bool, Optional[int]]:
        try:
            response: requests.Response = requests.get(url)
            up_status: bool = response.status_code < 400
            return up_status, response.status_code
        except requests.RequestException:
            return False, None
        
    def RunRequest(self, monitor_id: str, url: str, args: Tuple, out_queue: Queue, end_event: threading.Event):
        interval = args[0]
        while not end_event.is_set():
            data = self.NetRequest(url)
            print_time = time.asctime(time.localtime())
            out_queue.put(f"{print_time} | ID: {monitor_id} | http | {url} | Server Up: {data[0]} | Status Code: {data[1]}")
            time.sleep(interval)


class HttpsService(AbstractRequest):
    """The class governing the methods to perform a HTTPS check on a given server and to perform the periodic HTTPS check."""
    def __init__(self):
        pass

    def NetRequest(self, url: str, timeout: int) -> Tuple[bool, Optional[int], str]:
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
        
    def RunRequest(self, monitor_id: str, url: str, args: Tuple, out_queue: Queue, end_event: threading.Event):
        interval = args[0]
        while not end_event.is_set():
            data = self.NetRequest(url)
            print_time = time.asctime(time.localtime())
            out_queue.put(f"{print_time} | ID: {monitor_id} | https | {url} | Server Up: {data[0]} | Status Code: {data[1]}")
            time.sleep(interval)
        

class NtpService(AbstractRequest):
    """The class governing the methods to perform NTP checks on a given NTP server and to perform the periodic NTP checks."""
    def __init__(self):
        pass

    def NetRequest(self, server: str) -> Tuple[bool, Optional[str]]:
        client = ntplib.NTPClient()
        try:
            response = client.request(server, version=3)
            return True, ctime(response.tx_time)
        except (ntplib.NTPException, gaierror):
            return False, None
        
    def RunRequest(self, monitor_id: str, url: str, args: Tuple, out_queue: Queue, end_event: threading.Event):
        interval = args[0]
        while not end_event.is_set():
            data = self.NetRequest(url)
            print_time = time.asctime(time.localtime())
            out_queue.put(f"{print_time} | ID: {monitor_id} | ntp | {url} | Up: {data[0]} | Server time: {data[1]}")
            time.sleep(interval)
        

class DnsService(AbstractRequest):
    """The class governing the methods to perform DNS checks on a given server and to perform periodic DNS checks."""
    def __init__(self):
        pass

    def NetRequest(self, server: str, query: str, record_type: str) -> Tuple[bool, Optional[str]]:
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [socket.gethostbyname(server)]
            query_result = resolver.resolve(query, record_type)
            result = [str(rdata) for rdata in query_result]
            return True, result
        except (dns.exception.Timeout, dns.resolver.NoNameservers, dns.resolver.NoAnswer, gaierror) as exc:
            return False, f"Error during request: {exc}."
        
    def RunRequest(self, monitor_id: str, url: str, args: Tuple, out_queue: Queue, end_event: threading.Event):
        query, record_type, interval = args[0], args[1], args[2]
        while not end_event.is_set():
            data = self.NetRequest(url, query, record_type)
            print_time = time.asctime(time.localtime())
            out_queue.put(f"{print_time} | ID: {monitor_id} | dns | {url} | {query} | {record_type} | Up: {data[0]} | Data: {data[1]}")
            time.sleep(interval)


class TcpPortService(AbstractRequest):
    """The class governing methods to check a specific port on a specific server using TCP, and to perform the same check periodically."""
    def __init__(self):
        pass

    def NetRequest(self, ip_address: str, port: int) -> Tuple[bool, Optional[str]]:
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
        
    def RunRequest(self, monitor_id: str, url: str, args: Tuple, out_queue: Queue, end_event: threading.Event):
        port, interval = args[0], args[1]
        while not end_event.is_set():
            data = self.NetRequest(url, port)
            print_time = time.asctime(time.localtime())
            out_queue.put(f"{print_time} | ID: {monitor_id} | tcp | {url} | {port} | Open: {data[0]} | {data[1]}")
            time.sleep(interval)


class UdpPortService(AbstractRequest):
    """The class governing methods to check a specific port on a specific server using UDP, and to perform the same check periodically."""
    def __init__(self):
        pass

    def NetRequest(self, ip_address: str, port: int) -> Tuple[bool, Optional[str]]:
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

    def RunRequest(self, monitor_id: str, url: str, args: Tuple, out_queue: Queue, end_event: threading.Event):
        port, timeout, interval = args[0], args[1], args[2]
        while not end_event.is_set():
            data = self.NetRequest(url, port, timeout)
            print_time = time.asctime(time.localtime())
            out_queue.put(f"{print_time} | ID: {monitor_id} | udp | {url} | {port} | Open: {data[0]} | {data[1]}")
            time.sleep(interval)


class ICMPPacket:
    """The class governing methods to create a bespoke ICMP packet and to provide that packet with a correct checksum."""
    def __init__(self):
        pass

    def CreatePacket(self, icmp_type: int, icmp_code: int, sequence_num: int, data_size: int) -> bytes:
        """Creates an ICMP packet, requires an icmp_type, icmp_code, sequence_num, and data_size; returns a packet of bytes."""
        thread_id = threading.get_ident()
        proc_id = os.getpid()
        icmp_id = zlib.crc32(f"{thread_id}{proc_id}".encode()) & 0xffff
        header: bytes = struct.pack("bbHHh", icmp_type, icmp_code, 0, icmp_id, sequence_num)
        rand_char: str = random.choice(string.ascii_letters + string.digits)
        data: bytes = (rand_char * data_size).encode()
        check_sum = self.CalculateCheckSum(header + data)
        header = struct.pack("bbHHh", icmp_type, icmp_code, socket.htons(check_sum), icmp_id, sequence_num)
        return header + data
    
    def CalculateCheckSum(self, data: bytes) -> int:
        """Calculates a checksum for the given data; returns that checksum as an integer."""
        check_sum: int = 0
        for i in range(0, len(data), 2):
            curr_num: int = (data[i] << 8) + (data[i+1])
            check_sum += curr_num
        check_sum = (check_sum >> 16) + (check_sum & 0xffff)
        check_sum = ~check_sum & 0xffff
        return check_sum
