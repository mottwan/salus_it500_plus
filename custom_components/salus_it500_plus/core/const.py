from homeassistant.const import (
    # ATTR_BATTERY_LEVEL,
    # ATTR_TEMPERATURE,
    CONDUCTIVITY,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_TEMPERATURE,
    PERCENTAGE,
    TEMP_CELSIUS,
    )

from homeassistant.components.climate.const import (
    HVAC_MODE_COOL,
    # HVAC_MODE_DRY,
    # HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    # HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF
    )

DOMAINS = ['binary_sensor',
           'climate',
           'sensor']

# Binary_sensor
ATTR_ANGLE = 'angle'
CONF_INVERT_STATE = 'invert_state'
CONF_OCCUPANCY_TIMEOUT = 'occupancy_timeout'

# Climate
HVAC_MODES = [HVAC_MODE_HEAT, HVAC_MODE_OFF]

DOMAIN = "salus_thermostat"
CONF_DEBUG = "debug"


