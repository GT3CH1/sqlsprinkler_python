from dataclasses import dataclass, field, asdict

from typing import List

import requests
import aiohttp
from sqlsprinkler import API, Zone

class System:
    """ This class represents a SQL Sprinkler system. """
    zones = []
    system_state = False
    hostname = ""
    session = requests.Session()

    def __init__(self, hostname: str) -> None:
        self.hostname = hostname
        self.zones = []
        self.system_state = False

    def __post_init__(self) -> None:
        """
        Gets the zones from the hostname.
        :return: None
        """
        self.zones = self.get_zones()
        self.system_state = self.get_system_state()

    def _fetch_zones(self) -> List[Zone]:
        """
        Fetches the zones from the hostname.
        :return: A list of zones.
        """
        url = "{}/{}".format(self.hostname,API.ZONE_INFO_URL)
        request = self.session.get(url)
        zone_list = []
        for zone in request.json():
            new_zone = Zone()
            new_zone.host = self.hostname
            new_zone.name = zone['name']
            new_zone.gpio = zone['gpio']
            new_zone.time = zone['time']
            new_zone.enabled = zone['enabled']
            new_zone.auto_off = zone['auto_off']
            new_zone.system_order = zone['system_order']
            new_zone.state = zone['state']
            new_zone.id = zone['id']
            zone_list.append(new_zone)
        return zone_list

    def get_zones(self) -> List[Zone]:
        """
        Returns the zones in the system.
        :return: A list of zones.
        """
        self.zones = self._fetch_zones()
        return self.zones

    def get_system_state(self) -> bool:
        """
        Returns the system state.
        :return: The system state.
        """
        self._update_system_state()
        return self.state

    def update(self):
        """
        Updates the system.
        :return: None
        """
        self.zones = self._fetch_zones()
        self._update_system_state()

    async def update_async(self):
        """
        Fetches the zones from the hostname.
        :return: A list of zones.
        """
        url = "{}/{}".format(self.hostname,API.ZONE_INFO_URL)
        zone_list = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                for zone in await response.json():
                    new_zone = Zone()
                    new_zone.host = self.hostname
                    new_zone.name = zone['name']
                    new_zone.gpio = zone['gpio']
                    new_zone.time = zone['time']
                    new_zone.enabled = zone['enabled']
                    new_zone.auto_off = zone['auto_off']
                    new_zone.system_order = zone['system_order']
                    new_zone.state = zone['state']
                    new_zone.id = zone['id']
                    zone_list.append(new_zone)
                self.zones = zone_list
            url = "{}/{}".format(self.hostname,API.SYSTEM_STATE_URL)
            async with session.get(url) as response:
                request = await response.json()
                self.state = request["system_enabled"]


    def turn_on(self):
        self.set_system_state(True)

    def turn_off(self):
        self.set_system_state(False)

    async def turn_on_async(self)
        self.set_system_state_async(True)

    async def turn_on_async(self)
        self.set_system_state_async(False)

    def set_system_state(self, state: bool) -> None:
        """
        Sets the system state.
        :param state: The state to set.
        :return: None
        """
        url = "{}/{}".format(self.hostname,API.SYSTEM_STATE_URL)
        request = self.session.put(url, json={"system_enabled": state})
        if request.status_code != 200:
            raise Exception(f"Failed to set system state {state}")
        self._update_system_state()

    async def set_system_state_async(self,state: bool) -> None:
        url = "{}/{}".format(self.hostname,API.SYSTEM_STATE_URL)
        json={"system_enabled": state}
        async with aiohttp.ClientSession() as session:
            async with session.post(url,json) as response:
                status = await response.status_code
                if status_code != 200:
                    raise Exception(f"Failed to set system state {state}")
                else:
                    self.state = state

    def _update_system_state(self) -> None:
        """
        Fetches the system state from the hostname.
        """
        url = "{}/{}".format(self.hostname,API.SYSTEM_STATE_URL)
        request = self.session.get(url).json()
        self.state = request["system_enabled"]

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
                "Name": zone.name,
                "GPIO": zone.gpio,
                "Time": zone.time,
                "Enabled": zone.enabled,
                "Autooff": zone.auto_off,
                }
        request = self.session.post(f"{self.hostname}/{API.ZONE_URL}", json=zone_to_add)
        if request.status_code != 200:
            raise Exception(f"Failed to add zone {zone}")
        self.zones = self.get_zones()

    def delete_zone(self, zone_id: int) -> None:
        """
        Deletes a zone from the system.
        :param zone_id: The zone ID to delete.
        :return: None
        """
        request = self.session.delete(f"{self.hostname}/{API.ZONE_URL}", json={"id": zone_id})
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
        zone.update_other(zone_to_update)
        self.zones = self.get_zones()

    def update_zone_order(self, zone_order: List[int]) -> None:
        """
        Updates the order of the zones.
        :param: zone_order: The new order of the zones.
        :return: None
        """
        request = self.session.put(f"{self.hostname}/{API.ZONE_ORDER_URL}", json={"order": zone_order})
        if request.status_code != 200:
            raise Exception(f"Failed to update zone order {zone_order}")
        self.zones = self.get_zones()

