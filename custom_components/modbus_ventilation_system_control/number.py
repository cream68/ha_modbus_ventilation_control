from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MANUAL_OUTPUT,
    DEFAULT_MANUAL_OUTPUT,
    DOMAIN,
    MAX_MILLIAMP,
    MIN_MILLIAMP,
)
from .entity import VentilationEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    async_add_entities([ManualOutputNumber(coordinator, entry)])


class BaseMilliampNumber(VentilationEntity, NumberEntity):
    _attr_native_min_value = MIN_MILLIAMP
    _attr_native_max_value = MAX_MILLIAMP
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = "mA"
    _attr_mode = NumberMode.SLIDER
    _attr_entity_category = EntityCategory.DIAGNOSTIC


class ManualOutputNumber(BaseMilliampNumber):
    _attr_name = "Manuell mA"
    _attr_suggested_object_id = "lueftungsanlage_manuell_ma"
    _attr_entity_category = None

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_manual_output"

    @property
    def native_value(self) -> float:
        return float(self.entry.options.get(CONF_MANUAL_OUTPUT, DEFAULT_MANUAL_OUTPUT))

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_manual_output(value)
