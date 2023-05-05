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

    def update(self) -> None:
        """
        Updates the state of the zone.
        :return: None
        """
        # send request to API_ZONE_INFO_URL with ID
        url = "{}/{}/{}".format(self.host, API.ZONE_INFO_URL, self.id)
        request = requests.get(url)
        self.name = request.json()['name']
        self.gpio = request.json()['gpio']
        self.time = request.json()['time']
        self.enabled = request.json()['enabled']
        self.auto_off = request.json()['auto_off']
        self.system_order = request.json()['system_order']
        self.state = request.json()['state']

    def enable(self):
        self.enabled = True
        self.update_other(self)

    def disable(self):
        self.enabled = False
        self.update_other(self)

    def set_time(self, time: int) -> None:
        self.time = time
        self.update_other(self)

    def set_gpio(self, gpio: int) -> None:
        self.gpio = gpio
        self.update_other(self)

    def set_name(self, name: str) -> None:
        self.name = name
        self.update_other(self)

    def set_auto_off(self, auto_off: bool) -> None:
        self.auto_off = auto_off
        self.update_other(self)

    def set_system_order(self, system_order: int) -> None:
        self.system_order = system_order
        self.update_other(self)

    def update_other(self, other) -> None:
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
            "Name": self.name,
            "GPIO": self.gpio,
            "Time": self.time,
            "Enabled": self.enabled,
            "Autooff": self.auto_off,
            "SystemOrder": self.system_order
        }
        req = requests.put(f"{self.host}/{API.ZONE_UPDATE_URL}", json=zone_json)
        if req.status_code != 200:
            raise Exception(f"Zone did not update successfully ({req.status_code}). Payload: {zone_json}")
