# BALANCE EX v{{VERSION}}

This one can be used for some basics tests already. Logging works, balance disabling works.

Also logging angular acceleration and raw IMU stuff

Some additional config parameters like error response curve and more filters

Balance package. This is a first attempt based on the balance app just to get started. It compiles and loads, but is completely untested. All settings are there and there is also a QML-file that can be extended.

Most things should be similar to the regular balance app, except some of the time measurements as they are mostly based on seconds now. If there are problems when testing I would check the time measurements first.

## Development UI

The UI can be run with simulated VESC data, without VESC Tool or hardware:

```sh
cd balance_ex
make dev-ui
```

`gui/ui.dev.qml` injects mock command, configuration, and color implementations
into `gui/components/BalanceUi.qml`. The production `gui/ui.qml` injects the
VESC Tool implementations. Both entry points use aliased directory imports and
empty inline component references.

Run `make generate-qml-bundle` after changing the UI. It recursively expands
those references, merges their Qt/VESC imports, and writes the checked-in
`gui/ui.bundle.qml` required by the VESC package format. The regular package
build copies that bundle and substitutes its `{{VERSION}}` placeholder without
regenerating it.

## Generated settings

The typed settings model in `python/settings_data.py` generates
`balance_ex/conf/settings.xml` and `balance_ex/conf/datatypes.h`. Regenerate
both files after changing the model:

```sh
make generate-settings
```
