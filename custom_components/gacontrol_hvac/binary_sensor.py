"""Binary sensor platform for Gacontrol HVAC."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    heating_group = hass.data[DOMAIN][entry.entry_id]["heating_group"]

    sensors = [
        HeatingGroupBinarySensor(
            coordinator,
            heating_group,
            entry,
            "system_active",
            "System",
            BinarySensorDeviceClass.RUNNING,
        ),
        HeatingGroupBinarySensor(
            coordinator,
            heating_group,
            entry,
            "pump_command",
            "Pumpe Befehl",
            BinarySensorDeviceClass.RUNNING,
        ),
        HeatingGroupBinarySensor(
            coordinator,
            heating_group,
            entry,
            "pump_running",
            "Pumpe",
            BinarySensorDeviceClass.RUNNING,
        ),
        HeatingGroupBinarySensor(
            coordinator,
            heating_group,
            entry,
            "pump_fault",
            "Pumpenstörung",
            BinarySensorDeviceClass.PROBLEM,
        ),
        HeatingGroupBinarySensor(
            coordinator,
            heating_group,
            entry,
            "safety_limiter_active",
            "Sicherheitstemperaturbegrenzer",
            BinarySensorDeviceClass.PROBLEM,
        ),
        HeatingGroupBinarySensor(
            coordinator,
            heating_group,
            entry,
            "has_fault",
            "Störung",
            BinarySensorDeviceClass.PROBLEM,
        ),
    ]

    async_add_entities(sensors)


class HeatingGroupBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for heating group."""

    def __init__(
        self, coordinator, heating_group, entry, sensor_type, name, device_class
    ):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_name = f"{heating_group.name} {name}"
        self._attr_device_class = device_class
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return getattr(self._heating_group, self._sensor_type)
