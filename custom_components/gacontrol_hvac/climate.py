"""Climate platform for Gacontrol HVAC."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    heating_group = hass.data[DOMAIN][entry.entry_id]["heating_group"]

    async_add_entities([HeatingGroupClimate(coordinator, heating_group, entry)])


class HeatingGroupClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a heating group climate entity."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]

    def __init__(self, coordinator, heating_group, entry):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_name = f"{heating_group.name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self._heating_group.supply_temp

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self._heating_group.supply_temp_setpoint

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation mode."""
        if not self._heating_group.enabled:
            return HVACMode.OFF

        mode = self._heating_group.operating_mode
        if mode == "off":
            return HVACMode.OFF
        elif mode == "on":
            return HVACMode.HEAT
        else:
            return HVACMode.AUTO

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            self._heating_group.set_operating_mode("off")
            self._heating_group.set_enabled(False)
        elif hvac_mode == HVACMode.HEAT:
            self._heating_group.set_enabled(True)
            self._heating_group.set_operating_mode("on")
        elif hvac_mode == HVACMode.AUTO:
            self._heating_group.set_enabled(True)
            self._heating_group.set_operating_mode("auto")

        await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "return_temperature": self._heating_group.return_temp,
            "outside_temperature": self._heating_group.outside_temp,
            "outside_temperature_avg": self._heating_group.outside_temp_avg,
            "mixing_valve_position": self._heating_group.mixing_valve_position,
            "system_active": self._heating_group.system_active,
            "pump_command": self._heating_group.pump_command,
            "pump_running": self._heating_group.pump_running,
            "controller_output": self._heating_group.controller_output,
            "error_signal": self._heating_group.error_signal,
        }
