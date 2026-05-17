"""Config flow for the openSenseMap integration."""

from typing import Any

from opensensemap_api.exceptions import OpenSenseMapConnectionError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_validation as cv

from .const import CONF_STATION_ID, DOMAIN
from .coordinator import async_get_station_data

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_STATION_ID): cv.string})


class OpenSenseMapConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for openSenseMap."""

    VERSION = 1

    async def _async_validate_station(
        self, user_input: dict[str, Any]
    ) -> tuple[str, dict[str, str]]:
        """Validate a station and build the config entry data."""
        station_id = user_input[CONF_STATION_ID]
        station = await async_get_station_data(self.hass, station_id)

        if not (station_name := station.data.get("name")):
            raise StationNotFound

        await self.async_set_unique_id(station_id)
        self._abort_if_unique_id_configured()

        title = user_input.get(CONF_NAME, station_name)
        data = {CONF_STATION_ID: station_id}
        if name := user_input.get(CONF_NAME):
            data[CONF_NAME] = name

        return title, data

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        """Handle legacy YAML import."""
        try:
            title, data = await self._async_validate_station(import_data)
        except OpenSenseMapConnectionError:
            return self.async_abort(reason="cannot_connect")
        except StationNotFound:
            return self.async_abort(reason="station_not_found")

        return self.async_create_entry(title=title, data=data)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}

        try:
            title, data = await self._async_validate_station(user_input)
        except OpenSenseMapConnectionError:
            errors["base"] = "cannot_connect"
        except StationNotFound:
            errors["base"] = "station_not_found"
        else:
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class StationNotFound(Exception):
    """Raised when a station could not be validated."""
