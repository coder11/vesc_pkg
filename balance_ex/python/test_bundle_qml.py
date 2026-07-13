"""Tests for the single-document QML component bundler."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bundle_qml import BundleError, bundle_qml


class QmlBundlerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_recursively_expands_components_and_merges_imports(self) -> None:
        entrypoint = self.write(
            "ui.qml",
            '''import QtQuick 2.12
import Vedder.vesc.utility 1.0
import "components" as Components

Item {
    component PanelRef: Components.Panel {}
    PanelRef {}
}
''',
        )
        self.write(
            "components/Panel.qml",
            '''import QtQuick.Controls 2.12
import "nested" as Nested

Rectangle {
    component LabelRef: Nested.Label {}
    LabelRef {}
}
''',
        )
        self.write(
            "components/nested/Label.qml",
            '''import QtQuick 2.15

Text {
    text: "bundled"
}
''',
        )

        result = bundle_qml(entrypoint)

        self.assertTrue(result.startswith("// This file is auto-generated"))
        self.assertIn("import QtQuick 2.15", result)
        self.assertNotIn("import QtQuick 2.12", result)
        self.assertIn("import QtQuick.Controls 2.12", result)
        self.assertIn("import Vedder.vesc.utility 1.0", result)
        self.assertNotIn('import "components"', result)
        self.assertNotIn('import "nested"', result)
        self.assertIn("component PanelRef: Rectangle {", result)
        self.assertIn("component LabelRef: Text {", result)
        self.assertLess(
            result.index("component LabelRef"),
            result.index("component PanelRef"),
            "nested dependencies must be hoisted before their consumers",
        )
        self.assertNotIn("Components.Panel", result)
        self.assertNotIn("Nested.Label", result)

    def test_preserves_build_placeholders(self) -> None:
        entrypoint = self.write(
            "ui.qml",
            '''import QtQuick 2.12
Item { property string version: "{{VERSION}}" }
''',
        )
        result = bundle_qml(entrypoint)
        self.assertIn('property string version: "{{VERSION}}"', result)

    def test_shared_transitive_dependency_is_emitted_once(self) -> None:
        entrypoint = self.write(
            "ui.qml",
            '''import QtQuick 2.12
import "components" as Components
Item {
    component BalanceRef: Components.Balance {}
    component SharedRef: Components.Shared {}
    BalanceRef {}
    SharedRef {}
}
''',
        )
        self.write(
            "components/Balance.qml",
            '''import QtQuick 2.12
import "." as Components
Item {
    component GaugeRef: Components.Gauge {}
    component SharedRef: Components.Shared {}
    GaugeRef {}
    SharedRef {}
}
''',
        )
        self.write(
            "components/Gauge.qml",
            '''import QtQuick 2.12
import "." as Components
Rectangle {
    component SharedRef: Components.Shared {}
    SharedRef {}
}
''',
        )
        self.write(
            "components/Shared.qml",
            '''import QtQuick 2.12
Text { text: "shared" }
''',
        )

        result = bundle_qml(entrypoint)

        self.assertEqual(result.count("component SharedRef: Text {"), 1)
        self.assertLess(
            result.index("component SharedRef"), result.index("component GaugeRef")
        )
        self.assertLess(
            result.index("component GaugeRef"), result.index("component BalanceRef")
        )

    def test_reports_a_missing_component(self) -> None:
        entrypoint = self.write(
            "ui.qml",
            '''import QtQuick 2.12
import "components" as Components
Item {
    component MissingRef: Components.Missing {}
}
''',
        )
        with self.assertRaisesRegex(BundleError, "does not exist"):
            bundle_qml(entrypoint)

    def test_rejects_qualified_usage_without_reference_wrapper(self) -> None:
        entrypoint = self.write(
            "ui.qml",
            '''import QtQuick 2.12
import "components" as Components
Item { Components.Gauge {} }
''',
        )
        with self.assertRaisesRegex(BundleError, "no empty inline component"):
            bundle_qml(entrypoint)

    def test_reports_dependency_cycles(self) -> None:
        entrypoint = self.write(
            "ui.qml",
            '''import QtQuick 2.12
import "components" as Components
Item {
    component ARef: Components.A {}
}
''',
        )
        self.write(
            "components/A.qml",
            '''import QtQuick 2.12
import "." as Components
Item {
    component BRef: Components.B {}
}
''',
        )
        self.write(
            "components/B.qml",
            '''import QtQuick 2.12
import "." as Components
Item {
    component ARef: Components.A {}
}
''',
        )
        with self.assertRaisesRegex(BundleError, "cyclic QML"):
            bundle_qml(entrypoint)


if __name__ == "__main__":
    unittest.main()
