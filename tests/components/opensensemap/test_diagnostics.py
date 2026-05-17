"""Diagnostics tests for the openSenseMap integration."""

from syrupy.assertion import SnapshotAssertion

from homeassistant.core import HomeAssistant

from .conftest import MockOpenSenseMapStation

from tests.common import MockConfigEntry
from tests.components.diagnostics import get_diagnostics_for_config_entry
from tests.typing import ClientSessionGenerator


async def test_config_entry_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    mock_opensensemap: MockOpenSenseMapStation,
    setup_integration: MockConfigEntry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test diagnostics for a config entry."""
    assert (
        await get_diagnostics_for_config_entry(hass, hass_client, setup_integration)
        == snapshot
    )
