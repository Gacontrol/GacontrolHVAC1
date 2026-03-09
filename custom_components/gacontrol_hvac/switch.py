"""Switch platform for Gacontrol HVAC."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    heating_group = hass.data[DOMAIN][entry.entry_id]["heating_group"]

    switches = [
        HeatingGroupEnabledSwitch(coordinator, heating_group, entry),
    ]

    async_add_entities(switches)


class HeatingGroupEnabledSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable/disable heating group."""

    def __init__(self, coordinator, heating_group, entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._attr_unique_id = f"{entry.entry_id}_enabled"
        self._attr_name = f"{heating_group.name} Freigabe"
        self._attr_icon = "mdi:check-circle"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._heating_group.enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._heating_group.set_enabled(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._heating_group.set_enabled(False)
        await self.coordinator.async_request_refresh()
