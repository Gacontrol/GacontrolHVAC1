"""Constants for the Gacontrol HVAC integration."""

DOMAIN = "gacontrol_hvac"

CONF_MIN_SUPPLY_TEMP = "min_supply_temp"
CONF_MAX_SUPPLY_TEMP = "max_supply_temp"
CONF_OUTSIDE_TEMP_ON = "outside_temp_on"
CONF_OUTSIDE_TEMP_OFF = "outside_temp_off"
CONF_TEMP_AVERAGING_HOURS = "temp_averaging_hours"
CONF_P_GAIN = "p_gain"
CONF_I_GAIN = "i_gain"
CONF_PUMP_START_DELAY = "pump_start_delay"

DEFAULT_MIN_SUPPLY_TEMP = 25.0
DEFAULT_MAX_SUPPLY_TEMP = 65.0
DEFAULT_OUTSIDE_TEMP_ON = 15.0
DEFAULT_OUTSIDE_TEMP_OFF = 18.0
DEFAULT_TEMP_AVERAGING_HOURS = 24.0
DEFAULT_P_GAIN = 5.0
DEFAULT_I_GAIN = 0.5
DEFAULT_PUMP_START_DELAY = 10

ATTR_SUPPLY_TEMP = "supply_temp"
ATTR_RETURN_TEMP = "return_temp"
ATTR_OUTSIDE_TEMP_AVG = "outside_temp_avg"
ATTR_SUPPLY_TEMP_SETPOINT = "supply_temp_setpoint"
ATTR_MIXING_VALVE_POSITION = "mixing_valve_position"
ATTR_PUMP_RUNNING = "pump_running"
ATTR_PUMP_FAULT = "pump_fault"
ATTR_SAFETY_LIMITER = "safety_limiter"
ATTR_CONTROLLER_OUTPUT = "controller_output"
ATTR_ERROR_SIGNAL = "error_signal"

FAULT_PUMP_FAULT = "pump_fault"
FAULT_SAFETY_LIMITER = "safety_limiter"
FAULT_NO_FEEDBACK = "no_feedback"
FAULT_SYSTEM_ERROR = "system_error"
