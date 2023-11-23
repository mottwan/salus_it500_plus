from homeassistant.components.climate.const import (HVAC_MODE_HEAT, HVAC_MODE_OFF)

DOMAINS = ['binary_sensor',
           'climate',
           'sensor']

# Binary_sensor
ATTR_ANGLE = 'angle'
CONF_INVERT_STATE = 'invert_state'
CONF_OCCUPANCY_TIMEOUT = 'occupancy_timeout'

# Climate
HVAC_MODES = [HVAC_MODE_HEAT, HVAC_MODE_OFF]

DOMAIN = "salus_it500_plus"
CONF_DEBUG = "debug"
