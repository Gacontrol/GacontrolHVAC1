"""Select platform for Gacontrol HVAC."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
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
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    heating_group = hass.data[DOMAIN][entry.entry_id]["heating_group"]

    selects = [
        OperatingModeSelect(coordinator, heating_group, entry),
    ]

    async_add_entities(selects)


class OperatingModeSelect(CoordinatorEntity, SelectEntity):
    """Select entity for operating mode."""

    _attr_options = ["auto", "on", "off"]
    _attr_icon = "mdi:state-machine"

    def __init__(self, coordinator, heating_group, entry):
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._attr_unique_id = f"{entry.entry_id}_operating_mode"
        self._attr_name = f"{heating_group.name} Betriebsmodus"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def current_option(self) -> str:
        """Return the current operating mode."""
        return self._heating_group.operating_mode

    async def async_select_option(self, option: str) -> None:
        """Set the operating mode."""
        self._heating_group.set_operating_mode(option)
        await self.coordinator.async_request_refresh()
