"""Tests that validate() passes on shipped config files and catches problems."""
import pytest
import yaml
from pathlib import Path

from generators.base import BaseGenerator


class TestValidateShippedConfigs:
    def test_validate_config_de(self, generator_de):
        result = generator_de.validate()
        assert result["errors"] == [], f"German config errors: {result['errors']}"

    def test_validate_config_en(self, generator_en):
        result = generator_en.validate()
        assert result["errors"] == [], f"English config errors: {result['errors']}"


class TestValidateDetectsProblems:
    def _write_minimal_config(self, tmp_path, datapoints_override=None, translations=None):
        """Write minimal config tree and return config_dir path."""
        dp = datapoints_override or {"datapoints": {}}
        (tmp_path / "datapoints.yaml").write_text(yaml.dump(dp))

        trans_dir = tmp_path / "translations"
        trans_dir.mkdir()
        (trans_dir / "de.yaml").write_text(yaml.dump(translations or {}))

        tmpl_dir = tmp_path / "templates"
        tmpl_dir.mkdir()
        (tmpl_dir / "types.yaml").write_text(yaml.dump({"sensor": {}, "number": {}}))

        return str(tmp_path)

    def test_validate_warns_missing_translation(self, tmp_path):
        cfg_dir = self._write_minimal_config(
            tmp_path,
            datapoints_override={
                "datapoints": {
                    268: {"type": "sensor", "name_key": "nonexistent_key"},
                },
            },
            translations={"some_other_key": "Wert"},
        )
        gen = BaseGenerator(config_dir=cfg_dir, language="de")
        result = gen.validate()
        assert len(result["warnings"]) > 0
        assert "nonexistent_key" in result["warnings"][0]

    def test_validate_catches_bad_type(self, tmp_path):
        cfg_dir = self._write_minimal_config(
            tmp_path,
            datapoints_override={
                "datapoints": {
                    999: {"type": "totally_invalid_type"},
                },
            },
        )
        gen = BaseGenerator(config_dir=cfg_dir, language="de")
        result = gen.validate()
        assert any("unknown type" in e for e in result["errors"])

    def test_validate_jinja_syntax_error(self, tmp_path):
        cfg_dir = self._write_minimal_config(
            tmp_path,
            datapoints_override={
                "datapoints": {
                    500: {
                        "type": "sensor",
                        "command_template": "{{ value | int }",
                    },
                },
            },
        )
        gen = BaseGenerator(config_dir=cfg_dir, language="de")
        result = gen.validate()
        assert any("Jinja2 syntax error" in e for e in result["errors"])
