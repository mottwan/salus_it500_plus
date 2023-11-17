import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class SalusThermostatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    data = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            # Store the email and password in the instance variable `data`
            self.data.update({
                "email": user_input["email"],
                "password": user_input["password"]
            })
            # Proceed to the next step to add device IDs
            return await self.async_step_heating_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("email"): str,
                vol.Required("password"): str
            }),
            errors=errors
        )

    async def async_step_heating_options(self, user_input=None):
        """Handle the step to configure heating zones and water heating."""
        errors = {}

        if user_input is not None:
            # Update the data with heating options
            self.data.update({
                "second_heating_zone": user_input["second_heating_zone"],
                "water_heating": user_input["water_heating"]
            })
            # Proceed to the next step to add device IDs
            return await self.async_step_add_device()

        return self.async_show_form(
            step_id="heating_options",
            data_schema=vol.Schema({
                vol.Required("second_heating_zone", default=False): bool,
                vol.Required("water_heating", default=False): bool
            }),
            errors=errors
        )

    async def async_step_add_device(self, user_input=None):
        """Handle the step to add device IDs."""
        errors = {}

        if user_input is not None:
            # Add the device ID to the list in `data`
            device_id = user_input.get("device_id")
            if "device_ids" not in self.data:
                self.data["device_ids"] = []
            if device_id:
                self.data["device_ids"].append(device_id)

            # Ask the user if they want to add another device ID
            return await self.async_step_confirm_device()

        return self.async_show_form(
            step_id="add_device",
            data_schema=vol.Schema({
                vol.Required("device_id"): str
            }),
            errors=errors
        )

    async def async_step_confirm_device(self, user_input=None):
        """Ask the user if they want to add another device."""
        if user_input is not None:
            if user_input["add_another"]:
                # If the user wants to add another device, go back to the add_device step
                return await self.async_step_add_device()
            else:
                # If the user is done adding devices, create the config entry
                return self.async_create_entry(title="My Integration", data=self.data)

        return self.async_show_form(
            step_id="confirm_device",
            data_schema=vol.Schema({
                vol.Required("add_another", default=False): bool
            })
        )

    # Add additional steps if necessary