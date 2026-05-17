"""Fixtures for the openSenseMap integration tests."""

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.opensensemap.const import CONF_STATION_ID, DOMAIN
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry

TEST_STATION_ID = "5d4f91a7e1c3f3001a7b1234"
TEST_STATION_NAME = "Backyard"
TEST_CUSTOM_NAME = "Garden Air"


class MockOpenSenseMapStation:
    """Mock openSenseMap station."""

    def __init__(self, name: str = TEST_STATION_NAME) -> None:
        """Initialize the mock station."""
        self.data = {"name": name}
        self.pm2_5 = 12.5
        self.pm10 = 23.5
        self.temperature = 21.5
        self.humidity = 47.2
        self.air_pressure = 1001.3
        self.wind_speed = 3.2
        self.wind_direction = 180
        self.precipitation = 0.0
        self.illuminance = 1200
        self.uv = 2.4
        self.pm1_0 = 8.1
        self.get_data = AsyncMock()


@pytest.fixture
def mock_station() -> MockOpenSenseMapStation:
    """Return a mock openSenseMap station."""
    return MockOpenSenseMapStation()


@pytest.fixture
def mock_opensensemap(mock_station: MockOpenSenseMapStation):
    """Patch the openSenseMap client."""
    with patch(
        "homeassistant.components.opensensemap.coordinator.OpenSenseMap",
        return_value=mock_station,
    ):
        yield mock_station


@pytest.fixture
def mock_setup_entry() -> AsyncMock:
    """Mock setting up a config entry."""
    with patch(
        "homeassistant.components.opensensemap.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=TEST_STATION_NAME,
        unique_id=TEST_STATION_ID,
        data={CONF_STATION_ID: TEST_STATION_ID},
    )


@pytest.fixture
async def setup_integration(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> MockConfigEntry:
    """Set up the integration."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry
