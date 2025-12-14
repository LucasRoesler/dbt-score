"""Unit tests for the linting functionality."""

from unittest.mock import patch

import click
import pytest

from dbt_score.cli import FORMAT_TYPE
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
def test_lint_dbt_project_import_colon(mock_evaluation, manifest_path):
    """Test linting with a custom formatter using colon separator."""
    mock_evaluation.return_value = mock_evaluation

    lint_dbt_project(
        manifest_path=manifest_path,
        config=Config(),
        format="dbt_score.formatters.json_formatter:JSONFormatter",
    )

    mock_evaluation.evaluate.assert_called_once()


@patch("dbt_score.lint.Evaluation")
def test_lint_dbt_project_import_dot(mock_evaluation, manifest_path):
    """Test linting with a custom formatter using dot separator."""
    mock_evaluation.return_value = mock_evaluation

    lint_dbt_project(
        manifest_path=manifest_path,
        config=Config(),
        format="dbt_score.formatters.json_formatter.JSONFormatter",
    )

    mock_evaluation.evaluate.assert_called_once()


def test_lint_dbt_project_import_module_not_found(manifest_path):
    """Test that importing from a non-existent module raises ModuleNotFoundError."""
    with pytest.raises(ModuleNotFoundError):
        lint_dbt_project(
            manifest_path=manifest_path,
            config=Config(),
            format="non_existent_module:SomeClass",
        )


def test_lint_dbt_project_import_class_not_found(manifest_path):
    """Test that importing a non-existent class raises AttributeError."""
    with pytest.raises(AttributeError):
        lint_dbt_project(
            manifest_path=manifest_path,
            config=Config(),
            format="dbt_score.formatters.json_formatter:NonExistentClass",
        )


def test_lint_dbt_project_import_not_formatter(manifest_path):
    """Test that importing a non-Formatter class raises TypeError."""
    with pytest.raises(TypeError, match="is not a Formatter subclass"):
        lint_dbt_project(
            manifest_path=manifest_path,
            config=Config(),
            format="dbt_score.config:Config",
        )


# Tests for FormatParamType (CLI boundary)


def test_format_param_type_builtin():
    """Test that built-in format names return as strings."""
    assert FORMAT_TYPE.convert("plain", None, None) == "plain"
    assert FORMAT_TYPE.convert("json", None, None) == "json"
    assert FORMAT_TYPE.convert("manifest", None, None) == "manifest"
    assert FORMAT_TYPE.convert("ascii", None, None) == "ascii"


def test_format_param_type_custom_import():
    """Test that custom import paths return the formatter class."""
    result = FORMAT_TYPE.convert(
        "dbt_score.formatters.json_formatter:JSONFormatter", None, None
    )
    assert result is JSONFormatter


def test_format_param_type_invalid_import():
    """Test that invalid import paths raise BadParameter."""
    with pytest.raises(click.exceptions.BadParameter):
        FORMAT_TYPE.convert("non_existent_module:SomeClass", None, None)
