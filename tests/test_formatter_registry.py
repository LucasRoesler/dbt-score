"""Unit tests for the formatter registry."""


from dbt_score.config import Config
from dbt_score.formatter_registry import BUILTIN_FORMATTERS, FormatterRegistry
from dbt_score.formatters.ascii_formatter import ASCIIFormatter
from dbt_score.formatters.human_readable_formatter import HumanReadableFormatter
from dbt_score.formatters.json_formatter import JSONFormatter
from dbt_score.formatters.manifest_formatter import ManifestFormatter


def test_formatter_registry_builtin(default_config):
    """Ensure built-in formatters are loaded."""
    registry = FormatterRegistry(default_config)
    registry.load_all()

    assert registry.get("plain") is HumanReadableFormatter
    assert registry.get("manifest") is ManifestFormatter
    assert registry.get("ascii") is ASCIIFormatter
    assert registry.get("json") is JSONFormatter


def test_formatter_registry_builtin_formatters_dict():
    """Ensure BUILTIN_FORMATTERS dict contains expected entries."""
    assert BUILTIN_FORMATTERS == {
        "plain": HumanReadableFormatter,
        "manifest": ManifestFormatter,
        "ascii": ASCIIFormatter,
        "json": JSONFormatter,
    }


def test_formatter_registry_get_unknown(default_config):
    """Test that getting an unknown formatter returns None."""
    registry = FormatterRegistry(default_config)
    registry.load_all()

    assert registry.get("nonexistent") is None


def test_formatter_registry_discovery(default_config):
    """Ensure formatters can be found in a given namespace."""
    registry = FormatterRegistry(default_config)
    registry._load("tests.formatters")

    # Should find the test formatter in the tests.formatters namespace
    expected = "tests.formatters.custom_formatter.CustomTestFormatter"
    assert expected in registry.formatters


def test_formatter_registry_formatters_property(default_config):
    """Test the formatters property returns the internal dict."""
    registry = FormatterRegistry(default_config)
    registry.load_all()

    formatters = registry.formatters
    assert isinstance(formatters, dict)
    assert len(formatters) >= len(BUILTIN_FORMATTERS)


def test_formatter_registry_namespace_config():
    """Test loading formatters from configured namespaces."""
    config = Config()
    config.formatter_namespaces = ["tests.formatters"]

    registry = FormatterRegistry(config)
    registry.load_all()

    # Should have both built-ins and custom formatter
    assert registry.get("plain") is HumanReadableFormatter
    expected = "tests.formatters.custom_formatter.CustomTestFormatter"
    assert expected in registry.formatters


def test_formatter_registry_skips_imported_formatters(default_config):
    """Ensure formatters imported from other modules are not duplicated."""
    registry = FormatterRegistry(default_config)
    registry._load("tests.formatters")

    # The formatter should only be registered once under its original module
    formatter_names = list(registry.formatters.keys())
    custom_formatter_count = sum(
        1 for name in formatter_names if "CustomTestFormatter" in name
    )
    assert custom_formatter_count == 1


def test_formatter_registry_searches_rule_namespaces():
    """Test that formatters are also discovered in rule_namespaces."""
    config = Config()
    # Put the formatter namespace in rule_namespaces, not formatter_namespaces
    config.rule_namespaces = ["tests.formatters"]
    config.formatter_namespaces = []

    registry = FormatterRegistry(config)
    registry.load_all()

    # Should still find the custom formatter via rule_namespaces
    expected = "tests.formatters.custom_formatter.CustomTestFormatter"
    assert expected in registry.formatters
