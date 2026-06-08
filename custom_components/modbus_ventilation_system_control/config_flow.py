from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_HOST,
    CONF_POLL_INTERVAL,
    CONF_PORT,
    CONF_SLAVE_ID,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    NAME,
)


def _settings_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): str,
            vol.Required(CONF_PORT, default=defaults.get(CONF_PORT, DEFAULT_PORT)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=65535, step=1, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_SLAVE_ID, default=defaults.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=247, step=1, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(
                CONF_POLL_INTERVAL,
                default=defaults.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=5, max=3600, step=5, mode=selector.NumberSelectorMode.BOX)
            ),
        }
    )


class VentilationConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title=NAME, data={}, options=user_input)
        return self.async_show_form(step_id="user", data_schema=_settings_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return VentilationOptionsFlow(config_entry)


class VentilationOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            options = {**self._config_entry.options, **user_input}
            return self.async_create_entry(data=options)
        return self.async_show_form(step_id="init", data_schema=_settings_schema(dict(self._config_entry.options)))
