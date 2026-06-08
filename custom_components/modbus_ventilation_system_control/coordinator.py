from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from pymodbus.client import AsyncModbusTcpClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    CONF_HOST,
    CONF_MANUAL_OUTPUT,
    CONF_POLL_INTERVAL,
    CONF_PORT,
    CONF_SLAVE_ID,
    DEFAULT_MANUAL_OUTPUT,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    DOMAIN,
    MAX_MILLIAMP,
    MIN_MILLIAMP,
    MODBUS_REGISTER,
    NAME,
    NOTIFICATION_ID_ERROR,
    NOTIFICATION_TITLE,
)

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class VentilationData:
    current_output: float | None
    target_output: float
    connected: bool
    status: str
    last_error: str | None
    last_successful_read: datetime | None


class VentilationCoordinator(DataUpdateCoordinator[VentilationData]):
    """Handle Modbus IO and schedule logic."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=NAME,
            update_interval=timedelta(seconds=self._poll_interval(entry)),
        )
        self.entry = entry
        self._client: AsyncModbusTcpClient | None = None
        self._notified_error = False
        self._notified_workday = False

    async def async_shutdown(self) -> None:
        await self._async_close_client()

    async def async_apply_options(self, entry: ConfigEntry) -> None:
        """Apply updated config entry options live."""
        old_connection = self._connection_signature(self.entry)
        self.entry = entry
        self.update_interval = timedelta(seconds=self._poll_interval(entry))
        if old_connection != self._connection_signature(entry):
            await self._async_close_client()
        await self.async_request_refresh()

    async def async_update_options(self, updates: dict) -> None:
        new_options = {**self.entry.options, **updates}
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        updated = self.hass.config_entries.async_get_entry(self.entry.entry_id) or self.entry
        await self.async_apply_options(updated)

    async def async_set_manual_output(self, value: float) -> None:
        await self.async_update_options({CONF_MANUAL_OUTPUT: value})
        try:
            await self._async_write_output(value)
        except Exception as err:  # noqa: BLE001
            await self._async_notify_error(f"Manueller Schreibfehler: {err}")
        await self.async_request_refresh()

    async def async_force_refresh(self) -> None:
        await self.async_request_refresh()

    async def _async_update_data(self) -> VentilationData:
        previous = self.data if self.data is not None else VentilationData(
            current_output=None,
            target_output=self._manual_output,
            connected=False,
            status="unbekannt",
            last_error=None,
            last_successful_read=None,
        )

        target_output = self._manual_output

        try:
            current_output = await self._async_read_output()

            await self._async_clear_error_notification()
            status = "manuell"
            return VentilationData(
                current_output=current_output,
                target_output=target_output,
                connected=True,
                status=status,
                last_error=None,
                last_successful_read=dt_util.now(),
            )
        except Exception as err:  # noqa: BLE001
            message = str(err)
            await self._async_notify_error(message)
            return VentilationData(
                current_output=previous.current_output,
                target_output=target_output,
                connected=False,
                status="fehler",
                last_error=message,
                last_successful_read=previous.last_successful_read,
            )

    @property
    def _manual_output(self) -> float:
        return float(self.entry.options.get(CONF_MANUAL_OUTPUT, DEFAULT_MANUAL_OUTPUT))

    async def _async_ensure_client(self) -> AsyncModbusTcpClient:
        if self._client is None:
            self._client = AsyncModbusTcpClient(
                host=self.entry.options.get(CONF_HOST),
                port=int(self.entry.options.get(CONF_PORT, DEFAULT_PORT)),
                timeout=DEFAULT_TIMEOUT,
            )
        if not self._client.connected:
            connected = await self._client.connect()
            if not connected:
                raise ConnectionError("Verbindung zum Modbus-Gerät fehlgeschlagen")
        return self._client

    async def _async_close_client(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001
                pass
            self._client = None

    async def _async_modbus_call(self, method_name: str, **kwargs):
        client = await self._async_ensure_client()
        method = getattr(client, method_name)
        slave_id = int(self.entry.options.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID))
        for key in ("slave", "unit", "device_id"):
            try:
                return await method(**kwargs, **{key: slave_id})
            except TypeError as err:
                if f"unexpected keyword argument '{key}'" in str(err):
                    continue
                raise
        raise RuntimeError("Keine kompatible pymodbus slave-ID API gefunden")

    async def _async_read_output(self) -> float:
        response = await self._async_modbus_call(
            "read_holding_registers",
            address=MODBUS_REGISTER,
            count=1,
        )
        if response.isError():
            raise RuntimeError(f"Modbus-Lesefehler: {response}")
        return round(response.registers[0] / 1000.0, 3)

    async def _async_write_output(self, value: float) -> None:
        clamped = max(MIN_MILLIAMP, min(MAX_MILLIAMP, value))
        response = await self._async_modbus_call(
            "write_register",
            address=MODBUS_REGISTER,
            value=int(clamped * 1000),
        )
        if hasattr(response, "isError") and response.isError():
            raise RuntimeError(f"Modbus-Schreibfehler: {response}")


    async def _async_notify_error(self, message: str) -> None:
        if self._notified_error and self.data and self.data.last_error == message:
            return
        self._notified_error = True
        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": NOTIFICATION_TITLE,
                "message": message,
                "notification_id": f"{NOTIFICATION_ID_ERROR}_{self.entry.entry_id}",
            },
            blocking=True,
        )

    async def _async_clear_error_notification(self) -> None:
        if not self._notified_error:
            return
        self._notified_error = False
        await self.hass.services.async_call(
            "persistent_notification",
            "dismiss",
            {"notification_id": f"{NOTIFICATION_ID_ERROR}_{self.entry.entry_id}"},
            blocking=True,
        )

    @staticmethod
    def _poll_interval(entry: ConfigEntry) -> int:
        return int(entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))

    @staticmethod
    def _connection_signature(entry: ConfigEntry) -> tuple[str | None, int, int]:
        return (
            entry.options.get(CONF_HOST),
            int(entry.options.get(CONF_PORT, DEFAULT_PORT)),
            int(entry.options.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)),
        )
