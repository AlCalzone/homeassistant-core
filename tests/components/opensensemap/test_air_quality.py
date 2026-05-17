"""Tests for the openSenseMap air quality platform."""

from unittest.mock import patch

from opensensemap_api.exceptions import OpenSenseMapConnectionError

from homeassistant.components.air_quality import (
    ATTR_PM_10,
    DOMAIN as AIR_QUALITY_DOMAIN,
)
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import DOMAIN as HOMEASSISTANT_DOMAIN, HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component

from .conftest import TEST_STATION_ID


async def test_setup_entry(
    hass: HomeAssistant,
    mock_opensensemap,
    setup_integration,
) -> None:
    """Test setting up the air quality entity from a config entry."""
    state = hass.states.get("air_quality.backyard")

    assert state is not None
    assert state.state == "12.5"
    assert state.attributes[ATTR_PM_10] == 23.5
    assert state.attributes[ATTR_ATTRIBUTION] == "Data provided by openSenseMap"


async def test_yaml_import_success(
    hass: HomeAssistant,
    issue_registry: ir.IssueRegistry,
    mock_opensensemap,
) -> None:
    """Test YAML import creates a config entry and deprecation issue."""
    assert await async_setup_component(
        hass,
        AIR_QUALITY_DOMAIN,
        {
            AIR_QUALITY_DOMAIN: {
                "platform": "opensensemap",
                "station_id": TEST_STATION_ID,
            }
        },
    )
    await hass.async_block_till_done()

    assert len(hass.config_entries.async_entries("opensensemap")) == 1
    assert issue_registry.async_get_issue(
        HOMEASSISTANT_DOMAIN, "deprecated_yaml_opensensemap"
    )


async def test_yaml_import_failure(
    hass: HomeAssistant,
    issue_registry: ir.IssueRegistry,
) -> None:
    """Test YAML import failure creates a repair issue."""
    with patch(
        "homeassistant.components.opensensemap.config_flow.async_get_station_data",
        side_effect=OpenSenseMapConnectionError,
    ):
        assert await async_setup_component(
            hass,
            AIR_QUALITY_DOMAIN,
            {
                AIR_QUALITY_DOMAIN: {
                    "platform": "opensensemap",
                    "station_id": TEST_STATION_ID,
                }
            },
        )
        await hass.async_block_till_done()

    assert issue_registry.async_get_issue(
        "opensensemap", "deprecated_yaml_import_issue_cannot_connect"
    )
