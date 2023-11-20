import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .climate import SalusThermostat
from .core.const import DOMAINS, DOMAIN, CONF_DEBUG

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_DEBUG): cv.string,
    }, extra=vol.ALLOW_EXTRA),
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, hass_config: dict):
    """ setup """
    config = hass_config.get(DOMAIN) or {}

    hass.data[DOMAIN] = {
        'config': config,
        'debug': _LOGGER.level > 0  # default debug from Hass config
    }

    config.setdefault('devices', {})

    await _handle_device_remove(hass)

    return True


# async def async_setup_entry(hass, config_entry, async_add_entities):
#     """Set up the climate entity from the config entry."""
#     config = config_entry.data
#     email = config["email"]
#     password = config["password"]
#     device_ids = config["device_ids"]
#     second_heating_zone = config["second_heating_zone"]
#     water_heating = config["water_heating"]
#
#     # Create climate entities based on the configuration and add them
#     entities = []
#     for device_id in device_ids:
#         entity = SalusThermostat(email, password, device_id, second_heating_zone, water_heating)
#         entities.append(entity)
#
#     async_add_entities(entities, True)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Support Aqara Gateway."""

    # migrate data (also after first setup) to options
    if entry.data:
        hass.config_entries.async_update_entry(entry, data={},
                                               options=entry.data)

    await _setup_logger(hass)

    config = hass.data[DOMAIN]['config']

    hass.data[DOMAIN][entry.entry_id] = \
        entity = SalusThermostat(hass, **entry.options, config=config)

    # add update handler
    if not entry.update_listeners:
        entry.add_update_listener(async_update_options)

    # init setup for each supported domains
    for domain in DOMAINS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(
            entry, domain))

    entity.start()

    await hass.data[DOMAIN][entry.entry_id].async_connect()

    async def async_stop_mqtt(_event: Event):
        """Stop MQTT component."""
        await hass.data[DOMAIN][entry.entry_id].async_disconnect()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_stop_mqtt)

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """ Update Optioins if available """
    await hass.config_entries.async_reload(entry.entry_id)


async def _setup_logger(hass: HomeAssistant):
    entries = hass.config_entries.async_entries(DOMAIN)
    any_debug = any(e.options.get('debug') for e in entries)

    # only if global logging don't set
    if not hass.data[DOMAIN]['debug']:
        # disable log to console
        _LOGGER.propagate = not any_debug
        # set debug if any of integrations has debug
        _LOGGER.setLevel(logging.DEBUG if any_debug else logging.NOTSET)

    # if don't set handler yet
    if any_debug and not _LOGGER.handlers:
        handler = AqaraGatewayDebug(hass)
        _LOGGER.addHandler(handler)

        info = await hass.helpers.system_info.async_get_system_info()
        info.pop('timezone')
        _LOGGER.debug(f"SysInfo: {info}")
