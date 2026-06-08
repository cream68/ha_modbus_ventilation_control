from __future__ import annotations

from datetime import time

DOMAIN = "modbus_ventilation_system_control"
NAME = "modbus ventilation system control"
NOTIFICATION_TITLE = "modbus ventilation system control"

PLATFORMS = ["sensor", "number", "button"]

CONF_HOST = "host"
CONF_MANUAL_OUTPUT = "manual_output"
CONF_POLL_INTERVAL = "poll_interval"
CONF_PORT = "port"
CONF_SLAVE_ID = "slave_id"

DEFAULT_MANUAL_OUTPUT = 6.0
DEFAULT_POLL_INTERVAL = 60
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1

DEFAULT_TIMEOUT = 3.0
MAX_MILLIAMP = 20.0
MIN_MILLIAMP = 0.0
MODBUS_REGISTER = 0
NOTIFICATION_ID_ERROR = f"{DOMAIN}_error"
