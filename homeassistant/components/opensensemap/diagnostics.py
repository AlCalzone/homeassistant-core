"""Diagnostics support for the openSenseMap integration."""

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .coordinator import OpenSenseMapConfigEntry

TO_REDACT = {"coordinates", "currentLocation"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: OpenSenseMapConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    return {
        "config_entry": dict(entry.data),
        "data": async_redact_data(dict(entry.runtime_data.data.data), TO_REDACT),
    }
