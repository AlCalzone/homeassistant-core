"""Integrate E3/DC home power stations into Home Assistant."""

from e3dc_ess_modbus import E3dcPowerStation

from homeassistant.components.modbus import async_get_unit
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryError, HomeAssistantError

from .config_flow import create_modbus_params
from .const import DOMAIN, UNIT_ID
from .coordinator import E3dcConfigEntry, E3dcDataUpdateCoordinator, E3dcRuntimeData
from .holds import E3dcHolds

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: E3dcConfigEntry) -> None:
    """Set up E3/DC from a config entry."""
    try:
        unit = async_get_unit(hass, entry, create_modbus_params(entry.data), UNIT_ID)
    except HomeAssistantError as err:
        raise ConfigEntryError(
            translation_domain=err.translation_domain,
            translation_key=err.translation_key,
            translation_placeholders=err.translation_placeholders,
        ) from err
    device = E3dcPowerStation(unit)
    entry.async_on_unload(device.close)

    coordinator = E3dcDataUpdateCoordinator(hass, entry, device)
    # The first poll also reads the identity and probes which blocks the station serves
    await coordinator.async_config_entry_first_refresh()
    if device.serial_number != entry.unique_id:
        raise ConfigEntryError(
            translation_domain=DOMAIN,
            translation_key="serial_mismatch",
            translation_placeholders={
                "expected": str(entry.unique_id),
                "found": str(device.serial_number),
            },
        )

    holds = E3dcHolds(hass, entry, device)
    entry.runtime_data = E3dcRuntimeData(coordinator, holds)

    # Home Assistant doesn't unload entries when it stops
    async def _async_release_on_stop(event: Event) -> None:
        await holds.async_close()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_release_on_stop)
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)


async def async_unload_entry(hass: HomeAssistant, entry: E3dcConfigEntry) -> None:
    """Unload a config entry and hand every held setpoint back."""
    await hass.config_entries.async_unload_platforms_or_raise(entry, PLATFORMS)
    await entry.runtime_data.holds.async_close()
