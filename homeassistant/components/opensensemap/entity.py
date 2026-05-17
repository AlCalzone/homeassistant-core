"""Base entity for the openSenseMap integration."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import OpenSenseMapDataUpdateCoordinator


class OpenSenseMapEntity(CoordinatorEntity[OpenSenseMapDataUpdateCoordinator]):
    """Base openSenseMap entity."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: OpenSenseMapDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            configuration_url=(
                f"https://opensensemap.org/explore/{coordinator.config_entry.unique_id}"
            ),
            identifiers={(DOMAIN, coordinator.config_entry.unique_id)},
            manufacturer="openSenseMap",
            model=getattr(coordinator.data, "model", None),
            name=coordinator.config_entry.title,
        )
