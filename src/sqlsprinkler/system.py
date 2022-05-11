from dataclasses import dataclass, field, asdict

from typing import List

import requests

from sqlsprinkler import Zone, API


@dataclass
class System:
    """ This class represents a SQL Sprinkler system. """
    zones: List[Zone] = field(default_factory=list)
    system_state: bool = field(default_factory=bool)
    host: str = field(default_factory=str)

    def __post_init__(self) -> None:
        """
        Gets the zones from the host.
        :return: None
        """
        self.zones = self.get_zones()
        self.system_state = self.get_system_state()

    def _fetch_zones(self) -> List[Zone]:
        """
        Fetches the zones from the host.
        :return: A list of zones.
        """
        request = requests.get(f"{self.host}/{API.ZONE_INFO_URL}").json()
        zone_list = []
        for zone in request:
            zone_list.append(Zone(zone))
        return zone_list

    def get_zones(self) -> List[Zone]:
        """
        Returns the zones in the system.
        :return: A list of zones.
        """
        self._fetch_zones()
        return self.zones

    def get_system_state(self) -> bool:
        """
        Returns the system state.
        :return: The system state.
        """
        self._update_system_state()
        return self.state

    def set_system_state(self, state: bool) -> None:
        """
        Sets the system state.
        :param state: The state to set.
        :return: None
        """
        request = requests.put(f"{self.host}/{API.SYSTEM_STATE_URL}", json={"system_state": state})
        if request.status_code != 200:
            raise Exception(f"Failed to set system state {state}")
        self._update_system_state()

    def _update_system_state(self) -> None:
        """
        Fetches the system state from the host.
        """
        request = requests.get(f"{self.host}/{API.SYSTEM_STATE_URL}").json()
        self.state = request["system_state"]

    def update_zone_state(self, zone_id: int, state: bool) -> None:
        """
        Updates the state of a zone.
        :param zone_id: The zone ID to update.
        :param state: The state of the zone, True for on, False for off.
        :return: None
        """
        # Get the zone where the ID matches the one we want to update
        zone = self.get_zone_by_id(zone_id)
        if zone is None:
            raise Exception(f"Zone {zone_id} not found")
        if state:
            zone.turn_on()
        else:
            zone.turn_off()
        self._fetch_zones()

    def get_zone_by_id(self, zone_id: int) -> Zone:
        """ Gets a zone by id."""
        zone = next(filter(lambda zone: zone.id == zone_id, self.zones), None)
        return zone

    def add_zone(self, zone: Zone) -> None:
        """
        Adds a zone to the system.
        :param zone: The zone to add.
        :return: None
        """
        zone_to_add = {
            "name": zone.name,
            "gpio": zone.gpio,
            "time": zone.time,
            "enabled": zone.enabled,
            "auto_off": zone.auto_off,
        }
        request = requests.post(f"{self.host}/{API.ZONE_URL}", json=zone_to_add)
        if request.status_code != 200:
            raise Exception(f"Failed to add zone {zone}")
        self.zones = self.get_zones()

    def delete_zone(self, zone_id: int) -> None:
        """
        Deletes a zone from the system.
        :param zone_id: The zone ID to delete.
        :return: None
        """
        request = requests.delete(f"{self.host}/{API.ZONE_URL}", json={"id": zone_id})
        if request.status_code != 200:
            raise Exception(f"Failed to delete zone {zone_id}")

    def update_zone(self, zone: Zone) -> None:
        """
        Updates a zone in the system.
        :param zone: The zone to update.
        :return: None
        """
        zone_to_update = self.get_zone_by_id(zone.id)
        if zone_to_update is None:
            raise Exception(f"Zone {zone.id} not found")
        zone.update(zone_to_update)
        self.zones = self.get_zones()

    def update_zone_order(self, zone_order: List[int]) -> None:
        """
        Updates the order of the zones.
        :param: zone_order: The new order of the zones.
        :return: None
        """
        request = requests.put(f"{self.host}/{API.ZONE_ORDER_URL}", json={"order": zone_order})
        if request.status_code != 200:
            raise Exception(f"Failed to update zone order {zone_order}")
        self.zones = self.get_zones()

