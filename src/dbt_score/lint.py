"""Lint dbt metadata."""

from pathlib import Path
from typing import Iterable

from dbt_score.config import Config
from dbt_score.evaluation import Evaluation
from dbt_score.formatter_registry import FormatterRegistry
from dbt_score.formatters import Formatter
from dbt_score.models import ManifestLoader
from dbt_score.rule_registry import RuleRegistry
from dbt_score.scoring import Scorer


def lint_dbt_project(
    manifest_path: Path,
    config: Config,
    format: str | type[Formatter],
    select: Iterable[str] | None = None,
) -> Evaluation:
    """Lint dbt manifest."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}.")

    rule_registry = RuleRegistry(config)
    rule_registry.load_all()

    manifest_loader = ManifestLoader(manifest_path, select=select)

    if isinstance(format, str):
        formatter_registry = FormatterRegistry(config)
        formatter_registry.load_all()
        formatter_class = formatter_registry.get(format)
        if formatter_class is None:
            raise ValueError(f"Unknown formatter: {format}")
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
