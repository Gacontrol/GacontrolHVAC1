"""Config flow for Gacontrol HVAC integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_MIN_SUPPLY_TEMP,
    CONF_MAX_SUPPLY_TEMP,
    CONF_OUTSIDE_TEMP_ON,
    CONF_OUTSIDE_TEMP_OFF,
    CONF_TEMP_AVERAGING_HOURS,
    CONF_P_GAIN,
    CONF_I_GAIN,
    CONF_PUMP_START_DELAY,
    DEFAULT_MIN_SUPPLY_TEMP,
    DEFAULT_MAX_SUPPLY_TEMP,
    DEFAULT_OUTSIDE_TEMP_ON,
    DEFAULT_OUTSIDE_TEMP_OFF,
    DEFAULT_TEMP_AVERAGING_HOURS,
    DEFAULT_P_GAIN,
    DEFAULT_I_GAIN,
    DEFAULT_PUMP_START_DELAY,
)

_LOGGER = logging.getLogger(__name__)


class GacontrolHVACConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gacontrol HVAC."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input["name"])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required("name", default="Heizgruppe 1"): str,
                vol.Required(
                    CONF_MIN_SUPPLY_TEMP, default=DEFAULT_MIN_SUPPLY_TEMP
                ): vol.Coerce(float),
                vol.Required(
                    CONF_MAX_SUPPLY_TEMP, default=DEFAULT_MAX_SUPPLY_TEMP
                ): vol.Coerce(float),
                vol.Required(
                    CONF_OUTSIDE_TEMP_ON, default=DEFAULT_OUTSIDE_TEMP_ON
                ): vol.Coerce(float),
                vol.Required(
                    CONF_OUTSIDE_TEMP_OFF, default=DEFAULT_OUTSIDE_TEMP_OFF
                ): vol.Coerce(float),
                vol.Required(
                    CONF_TEMP_AVERAGING_HOURS, default=DEFAULT_TEMP_AVERAGING_HOURS
                ): vol.Coerce(float),
                vol.Required(CONF_P_GAIN, default=DEFAULT_P_GAIN): vol.Coerce(float),
                vol.Required(CONF_I_GAIN, default=DEFAULT_I_GAIN): vol.Coerce(float),
                vol.Required(
                    CONF_PUMP_START_DELAY, default=DEFAULT_PUMP_START_DELAY
                ): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> GacontrolHVACOptionsFlow:
        """Get the options flow for this handler."""
        return GacontrolHVACOptionsFlow(config_entry)


class GacontrolHVACOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Gacontrol HVAC."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_MIN_SUPPLY_TEMP,
                    default=self.config_entry.data.get(
                        CONF_MIN_SUPPLY_TEMP, DEFAULT_MIN_SUPPLY_TEMP
                    ),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_MAX_SUPPLY_TEMP,
                    default=self.config_entry.data.get(
                        CONF_MAX_SUPPLY_TEMP, DEFAULT_MAX_SUPPLY_TEMP
                    ),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_OUTSIDE_TEMP_ON,
                    default=self.config_entry.data.get(
                        CONF_OUTSIDE_TEMP_ON, DEFAULT_OUTSIDE_TEMP_ON
                    ),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_OUTSIDE_TEMP_OFF,
                    default=self.config_entry.data.get(
                        CONF_OUTSIDE_TEMP_OFF, DEFAULT_OUTSIDE_TEMP_OFF
                    ),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_TEMP_AVERAGING_HOURS,
                    default=self.config_entry.data.get(
                        CONF_TEMP_AVERAGING_HOURS, DEFAULT_TEMP_AVERAGING_HOURS
                    ),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_P_GAIN,
                    default=self.config_entry.data.get(CONF_P_GAIN, DEFAULT_P_GAIN),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_I_GAIN,
                    default=self.config_entry.data.get(CONF_I_GAIN, DEFAULT_I_GAIN),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_PUMP_START_DELAY,
                    default=self.config_entry.data.get(
                        CONF_PUMP_START_DELAY, DEFAULT_PUMP_START_DELAY
                    ),
                ): vol.Coerce(int),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
