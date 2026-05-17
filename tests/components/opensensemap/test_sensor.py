"""Tests for the openSenseMap sensor platform."""

from unittest.mock import patch

from opensensemap_api.exceptions import OpenSenseMapConnectionError
import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.const import STATE_UNAVAILABLE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import snapshot_platform


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensors(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    mock_config_entry,
    mock_opensensemap,
) -> None:
    """Test the sensor entities."""
    mock_config_entry.add_to_hass(hass)
    with patch("homeassistant.components.opensensemap.PLATFORMS", [Platform.SENSOR]):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


async def test_sensor_unavailable_logging(
    hass: HomeAssistant,
    mock_config_entry,
    mock_opensensemap,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test sensors become unavailable and log once when updates fail."""
    mock_config_entry.add_to_hass(hass)

    with patch("homeassistant.components.opensensemap.PLATFORMS", [Platform.SENSOR]):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("sensor.backyard_pm2_5")
    assert state is not None
    assert state.state != STATE_UNAVAILABLE

    mock_opensensemap.get_data.side_effect = OpenSenseMapConnectionError

    await mock_config_entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    state = hass.states.get("sensor.backyard_pm2_5")
    assert state is not None
    assert state.state == STATE_UNAVAILABLE
    assert caplog.text.count("Unable to fetch openSenseMap data for station") == 1

    caplog.clear()

    await mock_config_entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    assert "Unable to fetch openSenseMap data for station" not in caplog.text
