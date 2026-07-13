# QML component pattern

The package UI is split into normal QML files for development, then bundled
into `ui.bundle.qml` because a VESC package requires one QML document.

## Using a component

Import the directory with a capitalized alias:

```qml
import "components" as Components
```

Inside the root object, declare an empty inline component that points to the
QML file, then instantiate the inline component by its reference name:

```qml
Item {
    component GaugeRef: Components.Gauge {}

    GaugeRef {
        inputValue: 42
    }
}
```

Here, `Components.Gauge` resolves to `components/Gauge.qml`. The bundler
replaces the empty declaration with the root object from that file and removes
the local directory import.

Do not instantiate a local component directly as `Components.Gauge {}`. Every
local dependency must have an empty inline reference declaration so the
bundler can discover it.

## Nested components

Component files use the same pattern for their own dependencies:

```qml
import "." as Components

Rectangle {
    component CustomTextRef: Components.CustomText {}

    CustomTextRef {
        text: "Ready"
    }
}
```

The bundler follows these references recursively and hoists nested dependencies
before the components that use them. Components **must** be referenced using
this exact pattern:

```qml
component MyComponentNameRef: Components.MyComponentName {}
```

The declared reference can be instantiated any number of times.

Regular module imports such as `import QtQuick.Controls 2.12` are merged into
the generated document. If multiple files import the same module and alias,
the highest explicit version is retained. JavaScript file imports cannot be
bundled.

## Entrypoints and generation

- `ui.qml` is the production entrypoint and may contain build placeholders such
  as `{{VERSION}}`.
- `ui.dev.qml` is the development entrypoint and injects mock VESC objects.
- `ui.bundle.qml` is generated from `ui.qml` and is checked into Git.

After changing an entrypoint or component, regenerate the production bundle
from the `balance_ex` directory:

```sh
make generate-qml-bundle
```

This target runs the bundler CLI directly:

```sh
python3 python/bundle_qml.py gui/ui.qml gui/ui.bundle.qml
```

Bundling preserves `{{VERSION}}`. The regular package build copies the bundle
into `build/ui.gen.qml` and substitutes the version there.
