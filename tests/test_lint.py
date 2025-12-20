"""Unit tests for the linting functionality."""

from unittest.mock import patch

import pytest
from dbt_score.config import Config
from dbt_score.formatters.json_formatter import JSONFormatter
from dbt_score.lint import lint_dbt_project

# Tests for lint_dbt_project (SDK boundary)


@patch("dbt_score.lint.Evaluation")
def test_lint_dbt_project(mock_evaluation, manifest_path):
    """Test linting the dbt project with builtin formatter."""
    mock_evaluation.return_value = mock_evaluation

    lint_dbt_project(manifest_path=manifest_path, config=Config(), format="plain")

    mock_evaluation.evaluate.assert_called_once()


@patch("dbt_score.lint.Evaluation")
def test_lint_dbt_project_custom_formatter_class(mock_evaluation, manifest_path):
    """Test linting with a formatter class passed directly."""
    mock_evaluation.return_value = mock_evaluation

    lint_dbt_project(
        manifest_path=manifest_path,
        config=Config(),
        format=JSONFormatter,
    )

    mock_evaluation.evaluate.assert_called_once()


@patch("dbt_score.lint.Evaluation")
def test_lint_dbt_project_formatter_by_qualified_name(mock_evaluation, manifest_path):
    """Test linting with a custom formatter using fully qualified name."""
    config = Config()
    config.formatter_namespaces = ["tests.formatters"]

    mock_evaluation.return_value = mock_evaluation

    lint_dbt_project(
        manifest_path=manifest_path,
        config=config,
        format="tests.formatters.custom_formatter.CustomTestFormatter",
    )

    mock_evaluation.evaluate.assert_called_once()


def test_lint_dbt_project_unknown_formatter(manifest_path):
    """Test that using an unknown formatter raises ValueError."""
    with pytest.raises(ValueError, match="Unknown formatter"):
        lint_dbt_project(
            manifest_path=manifest_path,
            config=Config(),
            format="nonexistent_formatter",
        )


def test_lint_dbt_project_formatter_not_in_namespace(manifest_path):
    """Test that a formatter not in configured namespaces raises ValueError."""
    config = Config()
    # Don't add the tests.formatters namespace
    config.formatter_namespaces = []

    with pytest.raises(ValueError, match="Unknown formatter"):
        lint_dbt_project(
            manifest_path=manifest_path,
            config=config,
            format="tests.formatters.custom_formatter.CustomTestFormatter",
        )
