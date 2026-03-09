"""Heating Group controller for Gacontrol HVAC."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from collections import deque

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_MIN_SUPPLY_TEMP,
    CONF_MAX_SUPPLY_TEMP,
    CONF_OUTSIDE_TEMP_ON,
    CONF_OUTSIDE_TEMP_OFF,
    CONF_TEMP_AVERAGING_HOURS,
    CONF_P_GAIN,
    CONF_I_GAIN,
    CONF_PUMP_START_DELAY,
)

_LOGGER = logging.getLogger(__name__)


class HeatingGroup:
    """Representation of a heating group controller."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the heating group."""
        self.hass = hass
        self.entry = entry
        self._name = entry.data.get("name", "Heizgruppe 1")

        self._operating_mode = "auto"
        self._enabled = True
        self._system_active = False
        self._pump_command = False
        self._pump_running = False
        self._pump_fault = False
        self._safety_limiter_active = False
        self._pump_start_time = None

        self._supply_temp = 20.0
        self._return_temp = 20.0
        self._outside_temp = 15.0
        self._outside_temp_history = deque(maxlen=1000)
        self._outside_temp_avg = 15.0

        self._supply_temp_setpoint = 20.0
        self._mixing_valve_position = 0.0
        self._controller_output = 0.0
        self._error_signal = 0.0
        self._integral_term = 0.0

        self._faults = []
        self._last_update = datetime.now()

        self._last_valve_command = None

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def operating_mode(self) -> str:
        """Return the operating mode."""
        return self._operating_mode

    @property
    def enabled(self) -> bool:
        """Return if heating group is enabled."""
        return self._enabled

    @property
    def system_active(self) -> bool:
        """Return if system is active."""
        return self._system_active

    @property
    def supply_temp(self) -> float:
        """Return supply temperature."""
        return self._supply_temp

    @property
    def return_temp(self) -> float:
        """Return return temperature."""
        return self._return_temp

    @property
    def outside_temp(self) -> float:
        """Return outside temperature."""
        return self._outside_temp

    @property
    def outside_temp_avg(self) -> float:
        """Return averaged outside temperature."""
        return self._outside_temp_avg

    @property
    def supply_temp_setpoint(self) -> float:
        """Return supply temperature setpoint."""
        return self._supply_temp_setpoint

    @property
    def mixing_valve_position(self) -> float:
        """Return mixing valve position (0-100%)."""
        return self._mixing_valve_position

    @property
    def pump_command(self) -> bool:
        """Return pump command state."""
        return self._pump_command

    @property
    def pump_running(self) -> bool:
        """Return if pump is running."""
        return self._pump_running

    @property
    def pump_fault(self) -> bool:
        """Return if pump has fault."""
        return self._pump_fault

    @property
    def safety_limiter_active(self) -> bool:
        """Return if safety limiter is active."""
        return self._safety_limiter_active

    @property
    def controller_output(self) -> float:
        """Return controller output."""
        return self._controller_output

    @property
    def error_signal(self) -> float:
        """Return error signal."""
        return self._error_signal

    @property
    def faults(self) -> list:
        """Return active faults."""
        return self._faults

    @property
    def has_fault(self) -> bool:
        """Return if there are active faults."""
        return len(self._faults) > 0

    def set_operating_mode(self, mode: str) -> None:
        """Set operating mode."""
        if mode in ["auto", "on", "off"]:
            self._operating_mode = mode
            _LOGGER.info("Operating mode set to: %s", mode)

    def set_enabled(self, enabled: bool) -> None:
        """Set enabled state."""
        self._enabled = enabled
        _LOGGER.info("Heating group enabled: %s", enabled)

    def set_supply_temp(self, temp: float) -> None:
        """Set supply temperature reading."""
        self._supply_temp = temp

    def set_return_temp(self, temp: float) -> None:
        """Set return temperature reading."""
        self._return_temp = temp

    def set_outside_temp(self, temp: float) -> None:
        """Set outside temperature reading."""
        self._outside_temp = temp
        self._outside_temp_history.append((datetime.now(), temp))
        self._update_outside_temp_avg()

    def set_pump_running(self, running: bool) -> None:
        """Set pump running feedback."""
        self._pump_running = running

    def set_pump_fault(self, fault: bool) -> None:
        """Set pump fault signal."""
        self._pump_fault = fault
        if fault:
            self._add_fault("pump_fault", "Pumpenstörung erkannt")
        else:
            self._clear_fault("pump_fault")

    def set_safety_limiter(self, active: bool) -> None:
        """Set safety limiter state."""
        self._safety_limiter_active = active
        if active:
            self._add_fault("safety_limiter", "Sicherheitstemperaturbegrenzer ausgelöst")
            self._pump_command = False
            self._mixing_valve_position = 0.0
        else:
            self._clear_fault("safety_limiter")

    def _update_outside_temp_avg(self) -> None:
        """Update averaged outside temperature."""
        averaging_hours = self.entry.data.get(CONF_TEMP_AVERAGING_HOURS, 24.0)
        cutoff_time = datetime.now() - timedelta(hours=averaging_hours)

        recent_temps = [
            temp for time, temp in self._outside_temp_history if time >= cutoff_time
        ]

        if recent_temps:
            self._outside_temp_avg = sum(recent_temps) / len(recent_temps)

    def _calculate_supply_setpoint(self) -> float:
        """Calculate supply temperature setpoint from heating curve."""
        min_temp = self.entry.data.get(CONF_MIN_SUPPLY_TEMP, 25.0)
        max_temp = self.entry.data.get(CONF_MAX_SUPPLY_TEMP, 65.0)
        outside_temp_off = self.entry.data.get(CONF_OUTSIDE_TEMP_OFF, 18.0)

        if self._outside_temp_avg >= outside_temp_off:
            return min_temp

        outside_temp_range_min = -20.0
        temp_span = outside_temp_off - outside_temp_range_min
        ratio = (outside_temp_off - self._outside_temp_avg) / temp_span
        ratio = max(0.0, min(1.0, ratio))

        setpoint = min_temp + ratio * (max_temp - min_temp)
        return max(min_temp, min(max_temp, setpoint))

    def _check_turn_on_conditions(self) -> bool:
        """Check if heating group should turn on."""
        if not self._enabled:
            return False

        if self._operating_mode == "off":
            return False

        if self._operating_mode == "on":
            return True

        outside_temp_on = self.entry.data.get(CONF_OUTSIDE_TEMP_ON, 15.0)
        return self._outside_temp_avg < outside_temp_on

    def _check_turn_off_conditions(self) -> bool:
        """Check if heating group should turn off."""
        if not self._enabled:
            return True

        if self._operating_mode == "off":
            return True

        if self._operating_mode == "on":
            return False

        outside_temp_off = self.entry.data.get(CONF_OUTSIDE_TEMP_OFF, 18.0)
        return self._outside_temp_avg > outside_temp_off

    def _run_pi_controller(self, dt: float) -> None:
        """Run PI controller for supply temperature."""
        self._error_signal = self._supply_temp_setpoint - self._supply_temp

        p_gain = self.entry.data.get(CONF_P_GAIN, 5.0)
        i_gain = self.entry.data.get(CONF_I_GAIN, 0.5)

        p_term = p_gain * self._error_signal

        self._integral_term += i_gain * self._error_signal * dt
        self._integral_term = max(-100.0, min(100.0, self._integral_term))

        self._controller_output = p_term + self._integral_term
        self._controller_output = max(0.0, min(100.0, self._controller_output))

        self._mixing_valve_position = self._controller_output

    def _check_pump_feedback(self) -> None:
        """Check pump feedback after start."""
        if not self._pump_command:
            return

        if self._pump_start_time is None:
            return

        pump_start_delay = self.entry.data.get(CONF_PUMP_START_DELAY, 10)
        time_since_start = (datetime.now() - self._pump_start_time).total_seconds()

        if time_since_start > pump_start_delay and not self._pump_running:
            self._add_fault("no_feedback", "Keine Pumpenbetriebsmeldung")

    def _add_fault(self, fault_type: str, message: str) -> None:
        """Add a fault."""
        if not any(f["type"] == fault_type for f in self._faults):
            self._faults.append(
                {"type": fault_type, "message": message, "time": datetime.now()}
            )
            _LOGGER.warning("Fault added: %s - %s", fault_type, message)

    def _clear_fault(self, fault_type: str) -> None:
        """Clear a fault."""
        self._faults = [f for f in self._faults if f["type"] != fault_type]

    def _read_linked_entities(self) -> None:
        """Read values from linked external entities."""
        supply_entity = self.entry.data.get("supply_temp_entity", "")
        if supply_entity and supply_entity in self.hass.states.entity_ids():
            try:
                state = self.hass.states.get(supply_entity)
                if state and state.state not in ["unknown", "unavailable"]:
                    self._supply_temp = float(state.state)
            except (ValueError, TypeError):
                pass

        return_entity = self.entry.data.get("return_temp_entity", "")
        if return_entity and return_entity in self.hass.states.entity_ids():
            try:
                state = self.hass.states.get(return_entity)
                if state and state.state not in ["unknown", "unavailable"]:
                    self._return_temp = float(state.state)
            except (ValueError, TypeError):
                pass

        outside_entity = self.entry.data.get("outside_temp_entity", "")
        if outside_entity and outside_entity in self.hass.states.entity_ids():
            try:
                state = self.hass.states.get(outside_entity)
                if state and state.state not in ["unknown", "unavailable"]:
                    temp = float(state.state)
                    self._outside_temp = temp
                    self._outside_temp_history.append((datetime.now(), temp))
                    self._update_outside_temp_avg()
            except (ValueError, TypeError):
                pass

        pump_feedback_entity = self.entry.data.get("pump_feedback_entity", "")
        if pump_feedback_entity and pump_feedback_entity in self.hass.states.entity_ids():
            state = self.hass.states.get(pump_feedback_entity)
            if state and state.state in ["on", "off"]:
                self._pump_running = state.state == "on"

        pump_fault_entity = self.entry.data.get("pump_fault_entity", "")
        if pump_fault_entity and pump_fault_entity in self.hass.states.entity_ids():
            state = self.hass.states.get(pump_fault_entity)
            if state and state.state in ["on", "off"]:
                self.set_pump_fault(state.state == "on")

        safety_limiter_entity = self.entry.data.get("safety_limiter_entity", "")
        if safety_limiter_entity and safety_limiter_entity in self.hass.states.entity_ids():
            state = self.hass.states.get(safety_limiter_entity)
            if state and state.state in ["on", "off"]:
                self.set_safety_limiter(state.state == "on")

    async def _write_output_entities(self) -> None:
        """Write commands to linked output entities."""
        pump_output_entity = self.entry.data.get("pump_output_entity", "")
        if pump_output_entity and pump_output_entity in self.hass.states.entity_ids():
            domain = pump_output_entity.split(".")[0]
            service = "turn_on" if self._pump_command else "turn_off"
            try:
                await self.hass.services.async_call(
                    domain, service, {"entity_id": pump_output_entity}, blocking=False
                )
            except Exception as e:
                _LOGGER.error("Error controlling pump output: %s", e)

        valve_open_entity = self.entry.data.get("valve_open_output_entity", "")
        valve_close_entity = self.entry.data.get("valve_close_output_entity", "")

        if valve_open_entity and valve_close_entity:
            if (
                valve_open_entity in self.hass.states.entity_ids()
                and valve_close_entity in self.hass.states.entity_ids()
            ):
                valve_command = "open" if self._mixing_valve_position > 50 else "close"

                if valve_command != self._last_valve_command:
                    self._last_valve_command = valve_command
                    domain_open = valve_open_entity.split(".")[0]
                    domain_close = valve_close_entity.split(".")[0]

                    try:
                        if valve_command == "open":
                            await self.hass.services.async_call(
                                domain_open,
                                "turn_on",
                                {"entity_id": valve_open_entity},
                                blocking=False,
                            )
                            await self.hass.services.async_call(
                                domain_close,
                                "turn_off",
                                {"entity_id": valve_close_entity},
                                blocking=False,
                            )
                        else:
                            await self.hass.services.async_call(
                                domain_open,
                                "turn_off",
                                {"entity_id": valve_open_entity},
                                blocking=False,
                            )
                            await self.hass.services.async_call(
                                domain_close,
                                "turn_on",
                                {"entity_id": valve_close_entity},
                                blocking=False,
                            )
                    except Exception as e:
                        _LOGGER.error("Error controlling valve outputs: %s", e)

    async def async_update(self) -> dict:
        """Update heating group state."""
        now = datetime.now()
        dt = (now - self._last_update).total_seconds()
        self._last_update = now

        self._read_linked_entities()

        if self._safety_limiter_active:
            self._system_active = False
            self._pump_command = False
            self._mixing_valve_position = 0.0
            self._integral_term = 0.0
            await self._write_output_entities()
            return self._get_state()

        should_turn_on = self._check_turn_on_conditions()
        should_turn_off = self._check_turn_off_conditions()

        if should_turn_off:
            self._system_active = False
            self._pump_command = False
            self._integral_term = 0.0
            self._clear_fault("no_feedback")
        elif should_turn_on:
            self._system_active = True
            self._supply_temp_setpoint = self._calculate_supply_setpoint()

            if not self._pump_command:
                self._pump_command = True
                self._pump_start_time = now
            else:
                self._check_pump_feedback()

            if dt > 0:
                self._run_pi_controller(dt)

        await self._write_output_entities()

        return self._get_state()

    def _get_state(self) -> dict:
        """Get current state."""
        return {
            "name": self._name,
            "operating_mode": self._operating_mode,
            "enabled": self._enabled,
            "system_active": self._system_active,
            "supply_temp": self._supply_temp,
            "return_temp": self._return_temp,
            "outside_temp": self._outside_temp,
            "outside_temp_avg": self._outside_temp_avg,
            "supply_temp_setpoint": self._supply_temp_setpoint,
            "mixing_valve_position": self._mixing_valve_position,
            "pump_command": self._pump_command,
            "pump_running": self._pump_running,
            "pump_fault": self._pump_fault,
            "safety_limiter_active": self._safety_limiter_active,
            "controller_output": self._controller_output,
            "error_signal": self._error_signal,
            "faults": self._faults,
            "has_fault": self.has_fault,
        }
