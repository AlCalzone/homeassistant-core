"""The openSenseMap integration."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import OpenSenseMapConfigEntry, OpenSenseMapDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.AIR_QUALITY, Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: OpenSenseMapConfigEntry
) -> bool:
    """Set up openSenseMap from a config entry."""
    coordinator = OpenSenseMapDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: OpenSenseMapConfigEntry
) -> bool:
    """Unload an openSenseMap config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
