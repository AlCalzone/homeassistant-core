"""Data update coordinator for the openSenseMap integration."""

from datetime import timedelta

from opensensemap_api import OpenSenseMap
from opensensemap_api.exceptions import OpenSenseMapConnectionError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_STATION_ID, DOMAIN, LOGGER

type OpenSenseMapConfigEntry = ConfigEntry[OpenSenseMapDataUpdateCoordinator]


def _create_station(hass: HomeAssistant, station_id: str) -> OpenSenseMap:
    """Create the openSenseMap API client."""
    return OpenSenseMap(station_id, async_get_clientsession(hass))


async def async_get_station_data(hass: HomeAssistant, station_id: str) -> OpenSenseMap:
    """Fetch data for a station."""
    station = _create_station(hass, station_id)
    await station.get_data()
    return station


class OpenSenseMapDataUpdateCoordinator(DataUpdateCoordinator[OpenSenseMap]):
    """Coordinate openSenseMap data updates."""

    config_entry: OpenSenseMapConfigEntry

    def __init__(self, hass: HomeAssistant, entry: OpenSenseMapConfigEntry) -> None:
        """Initialize the coordinator."""
        self._station: OpenSenseMap | None = None
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {entry.title}",
            update_interval=timedelta(minutes=10),
        )

    async def _async_update_data(self) -> OpenSenseMap:
        """Fetch data from the openSenseMap API."""
        if self._station is None:
            self._station = _create_station(
                self.hass, self.config_entry.data[CONF_STATION_ID]
            )

        try:
            await self._station.get_data()
        except OpenSenseMapConnectionError as err:
            raise UpdateFailed(f"Unable to fetch openSenseMap data: {err}") from err

        if "name" not in self._station.data:
            raise UpdateFailed("Station is not available")

        return self._station
