from dataclasses import field, dataclass

import requests
from sqlsprinkler import API
@dataclass
class Zone:
    """ This class represents a SQL Sprinkler zone. """
    host = "none"
    name: str = field(default_factory=str)
    gpio: int = field(default_factory=int)
    time: int = field(default_factory=int)
    enabled: bool = field(default_factory=bool)
    auto_off: bool = field(default_factory=bool)
    system_order: int = field(default_factory=int)
    state: bool = field(default_factory=bool)
    id: int = field(default_factory=int)

    def turn_on(self) -> None:
        """
        Turns the zone on.
        :return: None
        """
        self.state = True
        # send request to API_ZONE_URL with ID and state
        url = "{}{}"
        requests.put(f"{self.host}/{API.ZONE_URL}", json={"id": self.id, "state": self.state})

    def turn_off(self) -> None:
        """
        Turns the zone off.
        :return: None
        """
        self.state = False
        # send request to API_ZONE_URL with ID and state
        requests.put(f"{self.host}/{API.ZONE_URL}", json={"id": self.id, "state": self.state})

    def update(self, other) -> None:
        """
        Updates the state of the zone.
        :param other: The zone to update with.
        :return: None
        """
        self.name = other.name
        self.gpio = other.gpio
        self.time = other.time
        self.enabled = other.enabled
        self.auto_off = other.auto_off
        self.system_order = other.system_order

        # send request to API_ZONE_UPDATE_URL with name, gpio, time, enabled, auto_off, system_order
        zone_json = {
            "id": self.id,
            "name": self.name,
            "gpio": self.gpio,
            "time": self.time,
            "enabled": self.enabled,
            "auto_off": self.auto_off,
            "system_order": self.system_order
        }
        requests.put(f"{self.host}/{API.ZONE_UPDATE_URL}", json=zone_json)
