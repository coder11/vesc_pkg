# BALANCE EX v{{VERSION}}-{{GIT_HASH}}

This one can be used for some basics tests already. Logging works, balance disabling works.

Also logging angular acceleration and raw IMU stuff

Some additional config parameters like error response curve and more filters

Balance package. This is a first attempt based on the balance app just to get started. It compiles and loads, but is completely untested. All settings are there and there is also a QML-file that can be extended.

Most things should be similar to the regular balance app, except some of the time measurements as they are mostly based on seconds now. If there are problems when testing I would check the time measurements first.

## Standalone UI

The UI can be run with simulated VESC data, without VESC Tool or hardware:

```sh
cd balance_ex
make test-ui
```

`gui/ui.test.qml` injects mock command, configuration, and color implementations
into `gui/components/BalanceUi.qml`. The production `gui/ui.qml` injects the
VESC Tool implementations. Both entry points use aliased directory imports and
empty inline component references.

The package build runs `python/bundle_qml.py`, which recursively expands those
references and merges their Qt/VESC imports into the single QML document
required by the VESC package format.
