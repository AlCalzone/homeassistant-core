"""Sensor platform for the openSenseMap integration."""

from collections.abc import Callable
from dataclasses import dataclass

from opensensemap_api import OpenSenseMap

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import OpenSenseMapConfigEntry
from .entity import OpenSenseMapEntity


@dataclass(kw_only=True, frozen=True)
class OpenSenseMapSensorEntityDescription(SensorEntityDescription):
    """Describe an openSenseMap sensor."""

    value_fn: Callable[[OpenSenseMap], float | int | None]


SENSOR_DESCRIPTIONS: tuple[OpenSenseMapSensorEntityDescription, ...] = (
    OpenSenseMapSensorEntityDescription(
        key="pm2_5",
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="pm2_5",
        value_fn=lambda station: station.pm2_5,
    ),
    OpenSenseMapSensorEntityDescription(
        key="pm10",
        device_class=SensorDeviceClass.PM10,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="pm10",
        value_fn=lambda station: station.pm10,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OpenSenseMapConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up openSenseMap sensors from a config entry."""
    async_add_entities(
        OpenSenseMapSensor(entry, description) for description in SENSOR_DESCRIPTIONS
    )


class OpenSenseMapSensor(OpenSenseMapEntity, SensorEntity):
    """Representation of an openSenseMap sensor."""

    entity_description: OpenSenseMapSensorEntityDescription

    def __init__(
        self,
        entry: OpenSenseMapConfigEntry,
        description: OpenSenseMapSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry.runtime_data)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

    @property
    def native_value(self) -> float | int | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
