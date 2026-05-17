"""Tests for the openSenseMap config flow."""

from unittest.mock import AsyncMock, patch

from opensensemap_api.exceptions import OpenSenseMapConnectionError

from homeassistant.components.opensensemap.const import CONF_STATION_ID, DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import (
    TEST_CUSTOM_NAME,
    TEST_STATION_ID,
    TEST_STATION_ID_2,
    TEST_STATION_NAME,
    TEST_STATION_NAME_2,
    MockOpenSenseMapStation,
)

from tests.common import MockConfigEntry


async def test_user_flow(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_opensensemap: MockOpenSenseMapStation,
) -> None:
    """Test the user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_STATION_ID: TEST_STATION_ID},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == TEST_STATION_NAME
    assert result["data"] == {CONF_STATION_ID: TEST_STATION_ID}


async def test_user_flow_cannot_connect(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test the user flow handles connection failures."""
    with patch(
        "homeassistant.components.opensensemap.config_flow.async_get_station_data",
        side_effect=OpenSenseMapConnectionError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_STATION_ID: TEST_STATION_ID},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_station_not_found(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_station: MockOpenSenseMapStation,
    mock_opensensemap: MockOpenSenseMapStation,
) -> None:
    """Test the user flow handles missing stations."""
    mock_station.data = {}

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_STATION_ID: TEST_STATION_ID},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "station_not_found"}


async def test_duplicate_station(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_config_entry: MockConfigEntry,
    mock_opensensemap: MockOpenSenseMapStation,
) -> None:
    """Test adding an already configured station."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_STATION_ID: TEST_STATION_ID},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_import_flow(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_opensensemap: MockOpenSenseMapStation,
) -> None:
    """Test importing YAML configuration."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_IMPORT},
        data={
            "platform": DOMAIN,
            CONF_STATION_ID: TEST_STATION_ID,
            "name": TEST_CUSTOM_NAME,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == TEST_CUSTOM_NAME
    assert result["data"] == {
        CONF_STATION_ID: TEST_STATION_ID,
        "name": TEST_CUSTOM_NAME,
    }


async def test_import_flow_cannot_connect(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test importing YAML handles connection failures."""
    with patch(
        "homeassistant.components.opensensemap.config_flow.async_get_station_data",
        side_effect=OpenSenseMapConnectionError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data={"platform": DOMAIN, CONF_STATION_ID: TEST_STATION_ID},
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"


async def test_import_flow_station_not_found(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_station: MockOpenSenseMapStation,
    mock_opensensemap: MockOpenSenseMapStation,
) -> None:
    """Test importing YAML handles unknown stations."""
    mock_station.data = {}

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_IMPORT},
        data={"platform": DOMAIN, CONF_STATION_ID: TEST_STATION_ID},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "station_not_found"


async def test_reconfigure_flow(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_config_entry: MockConfigEntry,
    mock_station: MockOpenSenseMapStation,
    mock_opensensemap: MockOpenSenseMapStation,
) -> None:
    """Test reconfiguring an entry."""
    mock_config_entry.add_to_hass(hass)
    mock_station.data["name"] = TEST_STATION_NAME_2

    result = await mock_config_entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_STATION_ID: TEST_STATION_ID_2},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.unique_id == TEST_STATION_ID_2
    assert mock_config_entry.title == TEST_STATION_NAME_2
    assert mock_config_entry.data == {CONF_STATION_ID: TEST_STATION_ID_2}


async def test_reconfigure_flow_already_configured(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_config_entry: MockConfigEntry,
    mock_opensensemap: MockOpenSenseMapStation,
) -> None:
    """Test reconfiguring to another configured station aborts."""
    second_entry = MockConfigEntry(
        domain=DOMAIN,
        title=TEST_STATION_NAME_2,
        unique_id=TEST_STATION_ID_2,
        data={CONF_STATION_ID: TEST_STATION_ID_2},
    )
    mock_config_entry.add_to_hass(hass)
    second_entry.add_to_hass(hass)

    result = await mock_config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_STATION_ID: TEST_STATION_ID_2},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
