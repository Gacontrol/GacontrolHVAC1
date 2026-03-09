"""Text platform for Gacontrol HVAC."""
from __future__ import annotations

from homeassistant.components.text import TextEntity
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
    """Set up the text platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    heating_group = hass.data[DOMAIN][entry.entry_id]["heating_group"]

    texts = [
        EntityLinkText(
            coordinator,
            heating_group,
            entry,
            "supply_temp_entity",
            "Vorlauftemperatur Entity",
            "Sensor für Vorlauftemperatur (z.B. sensor.vorlauf_temp)",
        ),
        EntityLinkText(
            coordinator,
            heating_group,
            entry,
            "return_temp_entity",
            "Rücklauftemperatur Entity",
            "Sensor für Rücklauftemperatur (z.B. sensor.ruecklauf_temp)",
        ),
        EntityLinkText(
            coordinator,
            heating_group,
            entry,
            "outside_temp_entity",
            "Außentemperatur Entity",
            "Sensor für Außentemperatur (z.B. sensor.aussen_temp)",
        ),
        EntityLinkText(
            coordinator,
            heating_group,
            entry,
            "pump_feedback_entity",
            "Pumpen Rückmeldung Entity",
            "Binärsensor für Pumpenbetriebsmeldung (z.B. binary_sensor.pumpe_laeuft)",
        ),
        EntityLinkText(
            coordinator,
            heating_group,
            entry,
            "pump_fault_entity",
            "Pumpenstörung Entity",
            "Binärsensor für Pumpenstörung (z.B. binary_sensor.pumpe_stoerung)",
        ),
        EntityLinkText(
            coordinator,
            heating_group,
            entry,
            "safety_limiter_entity",
            "Sicherheitstemperaturbegrenzer Entity",
            "Binärsensor für STB (z.B. binary_sensor.stb_aktiv)",
        ),
        EntityLinkText(
            coordinator,
            heating_group,
            entry,
            "pump_output_entity",
            "Pumpen Ausgang Entity",
            "Switch/Output für Pumpensteuerung (z.B. switch.pumpe_ausgang)",
        ),
        EntityLinkText(
            coordinator,
            heating_group,
            entry,
            "valve_open_output_entity",
            "Ventil AUF Ausgang Entity",
            "Output für Ventil AUF (z.B. switch.ventil_auf)",
        ),
        EntityLinkText(
            coordinator,
            heating_group,
            entry,
            "valve_close_output_entity",
            "Ventil ZU Ausgang Entity",
            "Output für Ventil ZU (z.B. switch.ventil_zu)",
        ),
    ]

    async_add_entities(texts)


class EntityLinkText(CoordinatorEntity, TextEntity):
    """Text entity for linking external entities."""

    _attr_icon = "mdi:link-variant"
    _attr_pattern = r"^[a-z_]+\.[a-z0-9_]+$"

    def __init__(self, coordinator, heating_group, entry, link_key, name, description):
        """Initialize the text entity."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._link_key = link_key
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{link_key}"
        self._attr_name = f"{heating_group.name} {name}"
        self._attr_entity_category = "config"
        self._description = description
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def native_value(self) -> str:
        """Return the current entity ID."""
        return self._entry.data.get(self._link_key, "")

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        return {
            "description": self._description,
        }

    async def async_set_value(self, value: str) -> None:
        """Set the entity ID."""
        value = value.strip()

        if value and not value.startswith(("sensor.", "binary_sensor.", "switch.", "input_boolean.", "number.", "input_number.")):
            return

        new_data = dict(self._entry.data)
        new_data[self._link_key] = value
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)
        await self.coordinator.async_request_refresh()
