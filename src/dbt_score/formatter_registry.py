"""Formatter registry.

This module implements formatter discovery.
"""

import importlib
import logging
import os
import pkgutil
import sys
from typing import Iterator

from dbt_score.config import Config
from dbt_score.formatters import Formatter
from dbt_score.formatters.ascii_formatter import ASCIIFormatter
from dbt_score.formatters.human_readable_formatter import HumanReadableFormatter
from dbt_score.formatters.json_formatter import JSONFormatter
from dbt_score.formatters.manifest_formatter import ManifestFormatter

logger = logging.getLogger(__name__)

# Built-in formatters with their short names
BUILTIN_FORMATTERS: dict[str, type[Formatter]] = {
    "plain": HumanReadableFormatter,
    "manifest": ManifestFormatter,
    "ascii": ASCIIFormatter,
    "json": JSONFormatter,
}


class FormatterRegistry:
    """A container for discovered formatters."""

    def __init__(self, config: Config) -> None:
        """Instantiate a formatter registry."""
        self.config = config
        self._formatters: dict[str, type[Formatter]] = {}

    @property
    def formatters(self) -> dict[str, type[Formatter]]:
        """Get all formatters."""
        return self._formatters

    def _walk_packages(self, namespace_name: str) -> Iterator[str]:
        """Walk packages and sub-packages recursively."""
        try:
            namespace = importlib.import_module(namespace_name)
        except ImportError:
            if namespace_name != "dbt_score_formatters":
                logger.warning(f"Can't import {namespace_name}.")
            return

        if not hasattr(namespace, "__path__"):
            # When called with a leaf, i.e. a module, don't attempt to iterate
            yield namespace_name
            return

        for package in pkgutil.walk_packages(
            namespace.__path__, namespace.__name__ + "."
        ):
            yield package.name

    def _load(self, namespace_name: str) -> None:
        """Load formatters found in a given namespace."""
        for module_name in self._walk_packages(namespace_name):
            module = importlib.import_module(module_name)
            for obj_name in dir(module):
                obj = module.__dict__[obj_name]
                # Skip objects imported from other modules
                # Note: using isinstance(obj, type) instead of type(obj) is type
                # because Formatter uses ABC, so subclasses have type ABCMeta
                if isinstance(obj, type) and module.__name__ != obj.__module__:
                    continue
                if (
                    isinstance(obj, type)
                    and issubclass(obj, Formatter)
                    and obj is not Formatter
                ):
                    self._add_formatter(obj)

    def _add_formatter(self, formatter_class: type[Formatter]) -> None:
        """Add a formatter to the registry."""
        # Register by fully qualified name (like rules)
        full_name = f"{formatter_class.__module__}.{formatter_class.__name__}"
        self._formatters[full_name] = formatter_class

    def load_all(self) -> None:
        """Load all formatters, built-in and custom."""
        old_sys_path = sys.path
        if self.config.inject_cwd_in_python_path and os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())

        # Load built-ins first
        for name, cls in BUILTIN_FORMATTERS.items():
            self._formatters[name] = cls

        # Load from configured namespaces (both formatter and rule namespaces)
        all_namespaces = set(self.config.formatter_namespaces) | set(
            self.config.rule_namespaces
        )
        for namespace in all_namespaces:
            self._load(namespace)

        sys.path = old_sys_path

    def get(self, name: str) -> type[Formatter] | None:
        """Get a formatter by name (short name or fully qualified)."""
        return self._formatters.get(name)
