"""Sensor platform for Gacontrol HVAC."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    heating_group = hass.data[DOMAIN][entry.entry_id]["heating_group"]

    sensors = [
        HeatingGroupTemperatureSensor(
            coordinator,
            heating_group,
            entry,
            "supply_temp",
            "Vorlauftemperatur",
        ),
        HeatingGroupTemperatureSensor(
            coordinator,
            heating_group,
            entry,
            "return_temp",
            "Rücklauftemperatur",
        ),
        HeatingGroupTemperatureSensor(
            coordinator,
            heating_group,
            entry,
            "outside_temp",
            "Außentemperatur",
        ),
        HeatingGroupTemperatureSensor(
            coordinator,
            heating_group,
            entry,
            "outside_temp_avg",
            "Außentemperatur (gemittelt)",
        ),
        HeatingGroupTemperatureSensor(
            coordinator,
            heating_group,
            entry,
            "supply_temp_setpoint",
            "Vorlauf Sollwert",
        ),
        HeatingGroupPercentageSensor(
            coordinator,
            heating_group,
            entry,
            "mixing_valve_position",
            "Mischventil Position",
        ),
        HeatingGroupPercentageSensor(
            coordinator,
            heating_group,
            entry,
            "controller_output",
            "Reglerausgang",
        ),
        HeatingGroupTemperatureSensor(
            coordinator,
            heating_group,
            entry,
            "error_signal",
            "Regelabweichung",
            show_state_class=False,
        ),
    ]

    async_add_entities(sensors)


class HeatingGroupTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Temperature sensor for heating group."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator,
        heating_group,
        entry,
        sensor_type,
        name,
        show_state_class=True,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_name = f"{heating_group.name} {name}"
        if show_state_class:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return getattr(self._heating_group, self._sensor_type)


class HeatingGroupPercentageSensor(CoordinatorEntity, SensorEntity):
    """Percentage sensor for heating group."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, heating_group, entry, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_name = f"{heating_group.name} {name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return getattr(self._heating_group, self._sensor_type)
