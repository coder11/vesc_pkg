"""Standard-library tests for the balance settings generator."""

from __future__ import annotations

import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from generate_settings import OUTPUT_PATH
from settings_data import XML, general, pid
from settings_schema import (
    Group,
    IntParameter,
    RawDescription,
    Separator,
    SettingsXml,
    Subgroup,
    TextDescription,
    ValidationError,
    collect_validation_issues,
    validate_settings,
)
from settings_xml import render_settings, write_settings


class SettingsGeneratorTests(unittest.TestCase):
    def test_settings_are_valid(self) -> None:
        validate_settings(XML)

    def test_magic_parameters_are_derived_from_root_properties(self) -> None:
        config_name, settings_name = XML.parameters[:2]
        self.assertEqual(config_name.name, "config_name")
        self.assertEqual(config_name.default, XML.config_name)
        self.assertEqual(settings_name.name, "hw_name")
        self.assertEqual(settings_name.long_name, XML.settings_name)

    def test_parameters_and_serialization_follow_group_order(self) -> None:
        self.assertIs(XML.parameters[2], general.balance_enabled)
        self.assertIs(XML.parameters[5], pid.pid_mode)
        expected = tuple(parameter.name for parameter in XML.parameters[2:])
        self.assertEqual(XML.serialization_order, expected)

    def test_text_and_raw_descriptions_are_rendered(self) -> None:
        root = ET.fromstring(render_settings(XML))
        params = root.find("Params")
        assert params is not None
        balance_description = params.findtext("balance_enabled/description") or ""
        error_description = params.findtext("error_linear_limit/description") or ""
        self.assertIsInstance(general.balance_enabled.description, TextDescription)
        self.assertIsInstance(general.error_linear_limit.description, RawDescription)
        self.assertIn("<html>", balance_description)
        self.assertIn("Enable/disable balancing.", balance_description)
        self.assertEqual(
            error_description, general.error_linear_limit.description.content
        )

    def test_checked_in_xml_matches_rendered_data(self) -> None:
        expected = OUTPUT_PATH.read_text(encoding="utf-8")
        self.assertEqual(render_settings(XML), expected)

    def test_invalid_data_does_not_replace_destination(self) -> None:
        invalid = SettingsXml(
            config_name="test_config",
            settings_name="Test Settings",
            groups=(
                Group(
                    name="Test",
                    subgroups=(
                        Subgroup(
                            name="Test",
                            items=(
                                IntParameter(
                                    name="too_large",
                                    long_name="Too large",
                                    maximum=65536,
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "settings.xml"
            destination.write_text("leave me intact\n", encoding="utf-8")
            with self.assertRaises(ValidationError):
                write_settings(invalid, destination)
            self.assertEqual(
                destination.read_text(encoding="utf-8"), "leave me intact\n"
            )

    def test_validation_aggregates_issues_from_model_classes(self) -> None:
        invalid = SettingsXml(
            config_name="not a C identifier",
            settings_name="",
            groups=(
                Group(
                    name="",
                    subgroups=(
                        Subgroup(
                            name="",
                            items=(
                                IntParameter(
                                    name="bad-name",
                                    long_name="",
                                    default=-1,
                                    minimum=100,
                                    maximum=70000,
                                    step=0,
                                    editor_scale=0.0,
                                ),
                                Separator(""),
                            ),
                        ),
                    ),
                ),
            ),
        )

        issues = collect_validation_issues(invalid)
        codes = {issue.code for issue in issues}
        self.assertGreaterEqual(len(issues), 10)
        self.assertIn("c_identifier", codes)
        self.assertIn("default_out_of_range", codes)
        self.assertIn("transport_range", codes)
        self.assertIn("positive_integer", codes)

        with self.assertRaises(ValidationError) as caught:
            invalid.validate()
        self.assertEqual(caught.exception.issues, issues)
        self.assertEqual(
            caught.exception.errors(), [issue.as_dict() for issue in issues]
        )
        self.assertIn("validation errors for SettingsXml", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
