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
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    DEGREE,
    LIGHT_LUX,
    PERCENTAGE,
    UV_INDEX,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import OpenSenseMapConfigEntry
from .entity import OpenSenseMapEntity

PARALLEL_UPDATES = 0


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
    OpenSenseMapSensorEntityDescription(
        key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="temperature",
        value_fn=lambda station: station.temperature,
    ),
    OpenSenseMapSensorEntityDescription(
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="humidity",
        value_fn=lambda station: station.humidity,
    ),
    OpenSenseMapSensorEntityDescription(
        key="air_pressure",
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="air_pressure",
        value_fn=lambda station: station.air_pressure,
    ),
    OpenSenseMapSensorEntityDescription(
        key="wind_speed",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="wind_speed",
        value_fn=lambda station: station.wind_speed,
    ),
    OpenSenseMapSensorEntityDescription(
        key="wind_direction",
        device_class=SensorDeviceClass.WIND_DIRECTION,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT_ANGLE,
        translation_key="wind_direction",
        value_fn=lambda station: station.wind_direction,
    ),
    OpenSenseMapSensorEntityDescription(
        key="precipitation",
        device_class=SensorDeviceClass.PRECIPITATION,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="precipitation",
        value_fn=lambda station: station.precipitation,
    ),
    OpenSenseMapSensorEntityDescription(
        key="illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=LIGHT_LUX,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="illuminance",
        value_fn=lambda station: station.illuminance,
    ),
    OpenSenseMapSensorEntityDescription(
        key="uv_index",
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UV_INDEX,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="uv_index",
        value_fn=lambda station: station.uv,
    ),
    OpenSenseMapSensorEntityDescription(
        key="pm1_0",
        device_class=SensorDeviceClass.PM1,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="pm1_0",
        value_fn=lambda station: station.pm1_0,
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
