from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME
from .coordinator import VentilationCoordinator


class VentilationEntity(CoordinatorEntity[VentilationCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: VentilationCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=NAME,
            manufacturer="Waveshare",
            model="DAC + Zeitsteuerung",
        )
