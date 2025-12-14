"""Lint dbt metadata."""

import importlib
from pathlib import Path
from typing import Iterable, Literal

from dbt_score.config import Config
from dbt_score.evaluation import Evaluation
from dbt_score.formatters import Formatter
from dbt_score.formatters.ascii_formatter import ASCIIFormatter
from dbt_score.formatters.human_readable_formatter import HumanReadableFormatter
from dbt_score.formatters.json_formatter import JSONFormatter
from dbt_score.formatters.manifest_formatter import ManifestFormatter
from dbt_score.models import ManifestLoader
from dbt_score.rule_registry import RuleRegistry
from dbt_score.scoring import Scorer

BUILTIN_FORMATTERS: dict[str, type[Formatter]] = {
    "plain": HumanReadableFormatter,
    "manifest": ManifestFormatter,
    "ascii": ASCIIFormatter,
    "json": JSONFormatter,
}

BuiltinFormat = Literal["plain", "manifest", "ascii", "json"]


def _import_formatter_class(import_path: str) -> type[Formatter]:
    """Import a formatter class from a string path.

    Supports both formats:
    - package.module:ClassName
    - package.module.ClassName
    """
    if ":" in import_path:
        module_path, class_name = import_path.rsplit(":", 1)
    else:
        module_path, class_name = import_path.rsplit(".", 1)

    module = importlib.import_module(module_path)
    formatter_class = getattr(module, class_name)

    if isinstance(formatter_class, type) and issubclass(formatter_class, Formatter):
        return formatter_class

    raise TypeError(f"{import_path} is not a Formatter subclass")


def lint_dbt_project(
    manifest_path: Path,
    config: Config,
    format: BuiltinFormat | type[Formatter],
    select: Iterable[str] | None = None,
) -> Evaluation:
    """Lint dbt manifest."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}.")

    rule_registry = RuleRegistry(config)
    rule_registry.load_all()

    manifest_loader = ManifestLoader(manifest_path, select=select)

    if isinstance(format, str):
        if format in BUILTIN_FORMATTERS:
            formatter_class = BUILTIN_FORMATTERS[format]
        else:
            formatter_class = _import_formatter_class(format)
    else:
        formatter_class = format
    formatter = formatter_class(manifest_loader=manifest_loader, config=config)

    scorer = Scorer(config)

    evaluation = Evaluation(
        rule_registry=rule_registry,
        manifest_loader=manifest_loader,
        formatter=formatter,
        scorer=scorer,
        config=config,
    )
    evaluation.evaluate()

    return evaluation
