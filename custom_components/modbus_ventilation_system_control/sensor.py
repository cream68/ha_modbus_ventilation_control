from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
)
from .entity import VentilationEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id].coordinator
    async_add_entities([
        CurrentOutputSensor(coordinator, entry),
        TargetOutputSensor(coordinator, entry),
        StatusSensor(coordinator, entry),
        LastReadSensor(coordinator, entry),
    ])


class CurrentOutputSensor(VentilationEntity, SensorEntity):
    _attr_name = "CH1 aktuell"
    _attr_native_unit_of_measurement = "mA"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_object_id = "lueftungsanlage_ch1_ausgang"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_output"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.current_output


class TargetOutputSensor(VentilationEntity, SensorEntity):
    _attr_name = "Zielwert"
    _attr_native_unit_of_measurement = "mA"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_suggested_object_id = "lueftungsanlage_zielwert"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_target_output"

    @property
    def native_value(self) -> float:
        return self.coordinator.data.target_output


class StatusSensor(VentilationEntity, SensorEntity):
    _attr_name = "Status"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_suggested_object_id = "lueftungsanlage_status"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self) -> str:
        return self.coordinator.data.status

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "connected": self.coordinator.data.connected,
            "last_error": self.coordinator.data.last_error,
        }


class LastReadSensor(VentilationEntity, SensorEntity):
    _attr_name = "Letzte Aktualisierung"
    _attr_device_class = "timestamp"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_suggested_object_id = "lueftungsanlage_letzte_aktualisierung"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_last_successful_read"

    @property
    def native_value(self):
        return self.coordinator.data.last_successful_read
