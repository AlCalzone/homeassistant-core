"""Support for openSenseMap air quality data."""

import voluptuous as vol

from homeassistant.components.air_quality import (
    PLATFORM_SCHEMA as AIR_QUALITY_PLATFORM_SCHEMA,
    AirQualityEntity,
)
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_NAME
from homeassistant.core import DOMAIN as HOMEASSISTANT_DOMAIN, HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import config_validation as cv, issue_registry as ir
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
    AddEntitiesCallback,
)
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_STATION_ID, DOMAIN, INTEGRATION_TITLE
from .coordinator import OpenSenseMapConfigEntry, OpenSenseMapDataUpdateCoordinator

PLATFORM_SCHEMA = AIR_QUALITY_PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_STATION_ID): cv.string, vol.Optional(CONF_NAME): cv.string}
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Import legacy YAML configuration into config entries."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_IMPORT},
        data=config,
    )

    if (
        result.get("type") is FlowResultType.ABORT
        and result.get("reason") != "already_configured"
    ):
        ir.async_create_issue(
            hass,
            DOMAIN,
            f"deprecated_yaml_import_issue_{result['reason']}",
            is_fixable=False,
            issue_domain=DOMAIN,
            severity=ir.IssueSeverity.WARNING,
            translation_key=f"deprecated_yaml_import_issue_{result['reason']}",
            translation_placeholders={
                "domain": DOMAIN,
                "integration_title": INTEGRATION_TITLE,
            },
        )
        return

    ir.async_create_issue(
        hass,
        HOMEASSISTANT_DOMAIN,
        f"deprecated_yaml_{DOMAIN}",
        is_fixable=False,
        issue_domain=DOMAIN,
        severity=ir.IssueSeverity.WARNING,
        translation_key="deprecated_yaml",
        translation_placeholders={
            "domain": DOMAIN,
            "integration_title": INTEGRATION_TITLE,
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: OpenSenseMapConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up openSenseMap air quality entities from a config entry."""
    async_add_entities([OpenSenseMapQuality(entry.runtime_data, entry.title)])


class OpenSenseMapQuality(
    CoordinatorEntity[OpenSenseMapDataUpdateCoordinator], AirQualityEntity
):
    """Implementation of an openSenseMap air quality entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self, coordinator: OpenSenseMapDataUpdateCoordinator, name: str
    ) -> None:
        """Initialize the air quality entity."""
        super().__init__(coordinator)
        self._name = name

    @property
    def name(self) -> str:
        """Return the name of the air quality entity."""
        return self._name

    @property
    def particulate_matter_2_5(self) -> float | None:
        """Return the particulate matter 2.5 level."""
        return self.coordinator.data.pm2_5

    @property
    def particulate_matter_10(self) -> float | None:
        """Return the particulate matter 10 level."""
        return self.coordinator.data.pm10
