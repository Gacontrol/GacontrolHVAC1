"""Number platform for Gacontrol HVAC."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    heating_group = hass.data[DOMAIN][entry.entry_id]["heating_group"]

    numbers = [
        HeatingGroupTemperatureInput(
            coordinator,
            heating_group,
            entry,
            "supply_temp",
            "Vorlauftemperatur Eingabe",
        ),
        HeatingGroupTemperatureInput(
            coordinator,
            heating_group,
            entry,
            "return_temp",
            "Rücklauftemperatur Eingabe",
        ),
        HeatingGroupTemperatureInput(
            coordinator,
            heating_group,
            entry,
            "outside_temp",
            "Außentemperatur Eingabe",
        ),
        HeatingCurveParameter(
            coordinator,
            heating_group,
            entry,
            "min_supply_temp",
            "Min. Vorlauftemperatur",
            5.0,
            50.0,
            25.0,
        ),
        HeatingCurveParameter(
            coordinator,
            heating_group,
            entry,
            "max_supply_temp",
            "Max. Vorlauftemperatur",
            30.0,
            90.0,
            65.0,
        ),
        HeatingCurveParameter(
            coordinator,
            heating_group,
            entry,
            "outside_temp_on",
            "Einschalttemperatur",
            -20.0,
            30.0,
            15.0,
        ),
        HeatingCurveParameter(
            coordinator,
            heating_group,
            entry,
            "outside_temp_off",
            "Ausschalttemperatur",
            -20.0,
            30.0,
            18.0,
        ),
        HeatingCurveParameter(
            coordinator,
            heating_group,
            entry,
            "temp_averaging_hours",
            "Mittelungszeit",
            1.0,
            168.0,
            24.0,
            "h",
        ),
        ControllerParameter(
            coordinator,
            heating_group,
            entry,
            "p_gain",
            "P-Anteil",
            0.0,
            50.0,
            5.0,
            0.1,
        ),
        ControllerParameter(
            coordinator,
            heating_group,
            entry,
            "i_gain",
            "I-Anteil",
            0.0,
            10.0,
            0.5,
            0.01,
        ),
        ControllerParameter(
            coordinator,
            heating_group,
            entry,
            "pump_start_delay",
            "Pumpen Start Verzögerung",
            0.0,
            300.0,
            10.0,
            1.0,
            "s",
        ),
    ]

    async_add_entities(numbers)


class HeatingGroupTemperatureInput(CoordinatorEntity, NumberEntity):
    """Number input for temperature values."""

    _attr_mode = NumberMode.BOX
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = -30.0
    _attr_native_max_value = 100.0
    _attr_native_step = 0.1

    def __init__(self, coordinator, heating_group, entry, input_type, name):
        """Initialize the number input."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._input_type = input_type
        self._attr_unique_id = f"{entry.entry_id}_{input_type}_input"
        self._attr_name = f"{heating_group.name} {name}"
        self._attr_icon = "mdi:thermometer"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return getattr(self._heating_group, self._input_type)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        if self._input_type == "supply_temp":
            self._heating_group.set_supply_temp(value)
        elif self._input_type == "return_temp":
            self._heating_group.set_return_temp(value)
        elif self._input_type == "outside_temp":
            self._heating_group.set_outside_temp(value)

        await self.coordinator.async_request_refresh()


class HeatingCurveParameter(CoordinatorEntity, NumberEntity):
    """Number entity for heating curve parameters."""

    _attr_mode = NumberMode.BOX
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator,
        heating_group,
        entry,
        param_key,
        name,
        min_value,
        max_value,
        default_value,
        unit=None,
    ):
        """Initialize the parameter."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._param_key = param_key
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{param_key}"
        self._attr_name = f"{heating_group.name} {name}"
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = 0.5
        self._default_value = default_value
        if unit:
            self._attr_native_unit_of_measurement = unit
        self._attr_icon = "mdi:tune"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._entry.data.get(f"CONF_{self._param_key.upper()}", self._default_value)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        new_data = dict(self._entry.data)
        new_data[f"CONF_{self._param_key.upper()}"] = value
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)
        await self.coordinator.async_request_refresh()


class ControllerParameter(CoordinatorEntity, NumberEntity):
    """Number entity for controller parameters."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator,
        heating_group,
        entry,
        param_key,
        name,
        min_value,
        max_value,
        default_value,
        step=0.1,
        unit=None,
    ):
        """Initialize the parameter."""
        super().__init__(coordinator)
        self._heating_group = heating_group
        self._param_key = param_key
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{param_key}"
        self._attr_name = f"{heating_group.name} {name}"
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._default_value = default_value
        if unit:
            self._attr_native_unit_of_measurement = unit
        self._attr_icon = "mdi:cog"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": heating_group.name,
            "manufacturer": "Gacontrol",
            "model": "HVAC Heating Group",
        }

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._entry.data.get(f"CONF_{self._param_key.upper()}", self._default_value)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        new_data = dict(self._entry.data)
        new_data[f"CONF_{self._param_key.upper()}"] = value
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)
        await self.coordinator.async_request_refresh()
