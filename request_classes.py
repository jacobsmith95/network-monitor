#
#
#


from typing import Tuple, Any 

class RequestService():
    #the abstract class defining the behavior of concrete request classes
    def runRequest():
        pass


class PingRequest(RequestService):
    #creates an ICMP packet and pings the given server
    def runRequest(host: str, ttl: int, timeout: int, sequence_number: int) -> Tuple[Any, float] | Tuple[Any, None]:
        pass