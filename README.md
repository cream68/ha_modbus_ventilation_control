# modbus ventilation system control

Custom integration for Home Assistant.

## HACS structure

```text
.
├── custom_components/
│   └── modbus_ventilation_system_control/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── number.py
│       ├── button.py
│       ├── entity.py
│       ├── const.py
│       ├── utils.py
│       └── translations/
├── hacs.json
└── README.md
```

## Notes

Local development runs from:

`config/custom_components/modbus_ventilation_system_control/`

For GitHub/HACS, only publish:

`custom_components/modbus_ventilation_system_control/`
