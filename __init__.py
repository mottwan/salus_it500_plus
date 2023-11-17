from .climate import SalusThermostat
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the climate entity from the config entry."""
    config = config_entry.data
    email = config["email"]
    password = config["password"]
    device_ids = config["device_ids"]
    second_heating_zone = config["second_heating_zone"]
    water_heating = config["water_heating"]

    # Create climate entities based on the configuration and add them
    entities = []
    for device_id in device_ids:
        entity = SalusThermostat(email, password, device_id, second_heating_zone, water_heating)
        entities.append(entity)

    async_add_entities(entities, True)