"""Support for E3/DC switches."""

from dataclasses import dataclass
from typing import Any, override

from e3dc_ess_modbus import Setpoint

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import E3dcConfigEntry
from .entity import E3dcSetpointDescription, E3dcSetpointEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class E3dcSetpointSwitchDescription(SwitchEntityDescription, E3dcSetpointDescription):
    """Describe a switch that holds a setpoint or hands it back."""


SETPOINT_SWITCHES: tuple[E3dcSetpointSwitchDescription, ...] = (
    E3dcSetpointSwitchDescription(
        key="battery_power_control",
        translation_key="battery_power_control",
        component="battery_control",
        setpoint=Setpoint.BATTERY_POWER,
    ),
    E3dcSetpointSwitchDescription(
        key="feed_in_limit_control",
        translation_key="feed_in_limit_control",
        component="grid_control",
        setpoint=Setpoint.FEED_IN_LIMIT,
    ),
    E3dcSetpointSwitchDescription(
        key="active_power_limit_control",
        translation_key="active_power_limit_control",
        component="grid_control",
        setpoint=Setpoint.ACTIVE_POWER_LIMIT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: E3dcConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the E3/DC switch platform."""
    runtime_data = entry.runtime_data
    device = runtime_data.coordinator.device
    served = {*device.readings_components, *device.settings_components}
    async_add_entities(
        E3dcSetpointSwitch(runtime_data, description)
        for description in SETPOINT_SWITCHES
        if description.component in served
    )


class E3dcSetpointSwitch(E3dcSetpointEntity, SwitchEntity):
    """On while the integration holds a setpoint.

    It is unknown while a rewrite or a hand-back fails, because the device
    may hold either state then.
    """

    entity_description: E3dcSetpointSwitchDescription

    @property
    @override
    def is_on(self) -> bool | None:
        if (hold := self._holds.get(self.entity_description.setpoint)) is None:
            return False
        return True if hold.confirmed else None

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._holds.async_resume(self.entity_description.setpoint)

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._holds.async_stop(self.entity_description.setpoint)
