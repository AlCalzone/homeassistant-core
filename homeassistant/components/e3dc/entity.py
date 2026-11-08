"""Base entity for E3/DC devices."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from e3dc_ess_modbus import Setpoint

from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import E3dcDataUpdateCoordinator, E3dcRuntimeData


class E3dcEntity(CoordinatorEntity[E3dcDataUpdateCoordinator]):
    """Defines a base E3/DC entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: E3dcDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        serial = coordinator.config_entry.unique_id
        if TYPE_CHECKING:
            assert serial is not None
        self._attr_unique_id = f"{serial}_{entity_description.key}"
        self._attr_device_info = coordinator.device_info


@dataclass(frozen=True, kw_only=True)
class E3dcSetpointDescription(EntityDescription):
    """Describe an entity for a setpoint the integration holds."""

    # The attribute of E3dcPowerStation the setpoint is written to, e.g. 'grid_control'
    component: str
    setpoint: Setpoint


class E3dcSetpointEntity(E3dcEntity):
    """An entity that shows a setpoint the integration holds."""

    entity_description: E3dcSetpointDescription

    def __init__(
        self,
        runtime_data: E3dcRuntimeData,
        entity_description: E3dcSetpointDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(runtime_data.coordinator, entity_description)
        self._holds = runtime_data.holds

    @override
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self._holds.async_add_listener(self.async_write_ha_state))

    @property
    @override
    def available(self) -> bool:
        """Always, because holding a setpoint doesn't depend on the last poll."""
        return True
