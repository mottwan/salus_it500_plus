"""
Adds support for the Salus Thermostat units.
"""
import datetime
import time
import logging
import re
import requests
import json

from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, TEMP_CELSIUS
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_OFF,
    CURRENT_HVAC_IDLE,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE

)

# Add new constants for additional features
SUPPORT_PRESETS = ["schedule", "manual", "holiday"]
SUPPORT_HVAC_MODES = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
SUPPORT_HOLIDAY_MODE = "holiday"
SUPPORT_SCHEDULE_PROGRAM = "schedule_program"
FROST_PROTECTION_MODE = "frost_protection"

URL_LOGIN = "https://salus-it500.com/public/login.php"
URL_GET_TOKEN = "https://salus-it500.com/public/control.php"
URL_GET_DATA = "https://salus-it500.com/public/ajax_device_values.php"
URL_SET_DATA = "https://salus-it500.com/includes/set.php"

DEFAULT_NAME = "Salus Thermostat"

CONF_NAME = "name"
MIN_TEMP = 5
MAX_TEMP = 34.5
SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE
SUPPORT_PRESET = ["schedule", "manual", "holiday"]

__version__ = "0.0.1"

_LOGGER = logging.getLogger(__name__)


# ... [existing PLATFORM_SCHEMA definition] ...

class SalusThermostat(ClimateEntity):

    def __init__(self, email, password, device_id, second_heating_zone, water_heating):
        """Initialize the thermostat."""
        self._online = None
        self._target_temp = None
        self._current_temp = None
        self._name = DEFAULT_NAME
        self._username = email
        self._password = password
        self._device_id = device_id
        self._current_temperature = None
        self._target_temperature = None
        self._frost = None
        self._status = None
        self._current_operation_mode = None
        self._token = None
        self._second_heating_zone = second_heating_zone
        self._water_heating = water_heating
        self._session = requests.Session()

        self.update()

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS | SUPPORT_PRESET

    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes."""
        return SUPPORT_HVAC_MODES

    @property
    def preset_modes(self):

        """Return a list of available preset modes."""
        return SUPPORT_PRESETS

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this thermostat."""
        return "_".join([self._name, "climate"])

    @property
    def should_poll(self):
        """Return if polling is required."""
        return True

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return MIN_TEMP

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return MAX_TEMP

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """ return current temperature """
        return self._current_temp

    @property
    def target_temperature(self):
        """ return target temperature """
        return self._target_temp

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return {
            # ... [other attributes] ...
            "online": self._online,
        }

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._set_temperature(temperature)

    def set_hvac_mode(self, hvac_mode):
        """Set HVAC mode, via URL commands."""

        headers = {"content-type": "application/x-www-form-urlencoded"}
        if hvac_mode == HVAC_MODE_OFF:
            payload = {"token": self._token, "devId": self._device_id, "auto": "1", "auto_setZ1": "1"}
            try:
                if self._session.post(URL_SET_DATA, data=payload, headers=headers):
                    self._current_operation_mode = "OFF"
            except:
                _LOGGER.error("Error Setting HVAC mode OFF.")
        elif hvac_mode == HVAC_MODE_HEAT:
            payload = {"token": self._token, "devId": self._device_id, "auto": "0", "auto_setZ1": "1"}
            try:
                if self._session.post(URL_SET_DATA, data=payload, headers=headers):
                    self._current_operation_mode = "ON"
            except:
                _LOGGER.error("Error Setting HVAC mode.")
        _LOGGER.info("Setting the HVAC mode.")

    def set_preset_mode(self, preset_mode):
        if preset_mode not in SUPPORT_PRESET:
            raise ValueError(f"Invalid preset mode: {preset_mode}")
        if preset_mode == "schedule":
            self._set_preset_schedule()
        elif preset_mode == "manual":
            self._set_preset_manual()
        elif preset_mode == "holiday":
            self._set_preset_holiday()
        elif preset_mode == "off":
            self._set_preset_off()
        self.schedule_update_ha_state(force_refresh=True)

    def set_holiday_mode(self, start_date, end_date):
        """Set the holiday mode with start and end dates."""
        # Implement the logic to set holiday mode using Salus API
        # ...

    def set_schedule_program(self, program_type, schedule=None):
        """Set the schedule program.

        :param program_type: Type of the program ('all', '5/2', 'individual')
        :param schedule: The schedule data, format depends on program_type
        """
        if program_type not in ['all', '5/2', 'individual']:
            _LOGGER.error("Invalid program type. Must be 'all', '5/2', or 'individual'.")
            return

        if program_type == 'all':
            self._set_all_days_schedule(schedule)
        elif program_type == '5/2':
            self._set_5_2_schedule(schedule)
        elif program_type == 'individual':
            self._set_individual_schedule(schedule)

    def _set_all_days_schedule(self, schedule):
        """Set the same schedule for all days."""
        # Implement the logic to set the same schedule for all days using Salus API
        # ...

    def _set_5_2_schedule(self, schedule):
        """Set one schedule for weekdays and another for the weekend."""
        # Implement the logic to set a 5/2 schedule using Salus API
        # ...

    def _set_individual_schedule(self, schedule):
        """Set individual schedules for each day."""
        # Implement the logic to set individual schedules for each day using Salus API
        # ...

    def override_target_temperature(self, temperature):
        """Override the current target temperature."""
        # Implement the logic to override target temperature using Salus API
        # ...

    def set_frost_protection(self, enabled, temperature=None):
        """Enable or disable frost protection mode.

        :param enabled: Boolean indicating whether to enable or disable frost protection.
        :param temperature: The temperature to maintain when frost protection is enabled.
        """
        if enabled and temperature is not None:
            # Validate the temperature
            if temperature < MIN_TEMP or temperature > MAX_TEMP:
                _LOGGER.error("Temperature for frost protection must be between %s and %s", MIN_TEMP, MAX_TEMP)
                return

            # Implement the logic to enable frost protection with the specified temperature using Salus API
            # ...

        elif not enabled:
            # Implement the logic to disable frost protection using Salus API
            # ...
            pass
        else:
            _LOGGER.error("Temperature must be provided to enable frost protection.")

    def _set_temperature(self, temperature):
        """Set new target temperature, via URL commands."""
        payload = {"token": self._token, "devId": self._device_id, "tempUnit": "0", "current_tempZ1_set": "1",
                   "current_tempZ1": temperature}
        headers = {"content-type": "application/x-www-form-urlencoded"}
        try:
            if self._session.post(URL_SET_DATA, data=payload, headers=headers):
                self._target_temperature = temperature
                # self.schedule_update_ha_state(force_refresh=True)
            _LOGGER.info("Salusfy set_temperature OK")
        except:
            _LOGGER.error("Error Setting the temperature.")

    def _set_preset_schedule(self):
        """Set the thermostat to the home preset."""
        # Set the temperature and other settings for the home preset
        # using the Salus API

    def _set_preset_manual(self):
        """Set the thermostat to the away preset."""
        # Set the temperature and other settings for the away preset
        # using the Salus API

    def _set_preset_holiday(self):
        """Set the thermostat to the sleep preset."""
        # Set the temperature and other settings for the sleep preset
        # using the Salus API

    def _set_preset_off(self):
        """Set the thermostat to the off preset."""
        # Set the temperature and other settings for the sleep preset
        # using the Salus API        

    def get_token(self):
        """Get the Session Token of the Thermostat."""
        payload = {"IDemail": self._username, "password": self._password, "login": "Login", "keep_logged_in": "1"}
        headers = {"content-type": "application/x-www-form-urlencoded"}

        try:
            self._session.post(URL_LOGIN, data=payload, headers=headers)
            params = {"devId": self._device_id}
            getTkoken = self._session.get(URL_GET_TOKEN, params=params)
            result = re.search('<input id="token" type="hidden" value="(.*)" />', getTkoken.text)
            _LOGGER.info("Salusfy get_token OK")
            self._token = result.group(1)
        except:
            _LOGGER.error("Error Geting the Session Token.")

    def _get_data(self):
        if self._token is None:
            self.get_token()
        params = {"devId": self._device_id, "token": self._token, "&_": str(int(round(time.time() * 1000)))}
        try:
            r = self._session.get(url=URL_GET_DATA, params=params)
            try:
                if r:
                    data = json.loads(r.text)
                    _LOGGER.info("Salusfy get_data output " + r.text)
                    self._target_temperature = float(data["CH1currentSetPoint"])
                    self._current_temperature = float(data["CH1currentRoomTemp"])
                    self._frost = float(data["frost"])

                    status = data['CH1heatOnOffStatus']
                    if status == "1":
                        self._status = "ON"
                    else:
                        self._status = "OFF"
                    mode = data['CH1heatOnOff']
                    if mode == "1":
                        self._current_operation_mode = "OFF"
                    else:
                        self._current_operation_mode = "ON"
                else:
                    _LOGGER.error("Could not get data from Salus.")
            except:
                self.get_token()
                self._get_data()
        except:
            _LOGGER.error("Error Geting the data from Web. Please check the connection to salus-it500.com manually.")

    def update(self):
        """Get the latest data."""
        self._get_data()
