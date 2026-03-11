#
#
#

import json
from abc import ABC, abstractmethod

def main():
    pass


class AbstractClient(ABC):
    """ """
    @abstractmethod
    def ReadSettings():
        pass

    @abstractmethod
    def WriteSettings():
        pass

    @abstractmethod
    def CommsHandler():
        pass

    @abstractmethod
    def ServicesHandler():
        pass

    @abstractmethod
    def ExitProgram():
        pass


class RemoteClient(AbstractClient):
    """ """
    def ReadSettings(monitor_id: str) -> str:
        with open(f"monitor_config_{monitor_id}.txt", "r") as file:
            config = json.load(file)
        file.close()
        return config
    
    def WriteSettings(monitor_id: str, config: str) -> None:
        with open(f"monitor_config_{monitor_id}.txt", "w") as file:
            json.dump(config, file)
        file.close()
        return


if __name__ == "__main__":
    main()