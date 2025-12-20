# Programmatic invocations

`dbt-score` can be used interactively as a CLI tool, but also be integrated in
Continuous Integration systems and anywhere else it makes sense.

## Machine-readable output

In order to programmatically use the output of `dbt-score` in another program,
the JSON formatter can be used:

```shell
$ dbt-score lint --format json
{
  "models": {
    "model1": {
      "score": 8.666666666666668,
      "badge": "🥈",
      "pass": true,
      "results": {
        "dbt_score.rules.generic.columns_have_description": {
          "result": "OK",
          "severity": "medium",
          "message": null
        },
        "dbt_score.rules.generic.has_description": {
          "result": "OK",
          "severity": "medium",
          "message": null
        },
        "dbt_score.rules.generic.has_owner": {
          "result": "WARN",
          "severity": "medium",
          "message": "Model lacks an owner."
        },
        "dbt_score.rules.generic.has_example_sql": {
          "result": "OK",
          "severity": "low",
          "message": null
        },
        "dbt_score.rules.generic.sql_has_reasonable_number_of_lines": {
          "result": "OK",
          "severity": "medium",
          "message": null
        }
      }
    }
  },
  "project": {
    "score": 8.666666666666668,
    "badge": "🥈",
    "pass": true
  }
}
```

## Custom formatters

For advanced use cases, you can create and use custom formatters. This works
similarly to how custom rules are discovered: formatters are loaded from
configured namespaces.

### Configuration

Formatters are discovered in both `rule_namespaces` and `formatter_namespaces`.
This means if you already have custom rules, you can place formatters in the same
package without additional configuration.

```toml
[tool.dbt-score]
# Formatters will be discovered here too
rule_namespaces = ["mypackage"]

# Optional: additional formatter-only namespaces
formatter_namespaces = ["dbt_score_formatters"]
```

By default, `dbt-score` looks for formatters in `dbt_score_formatters` and the
default rule namespaces (`dbt_score.rules`, `dbt_score_rules`).

### Creating a custom formatter

Custom formatters must subclass `dbt_score.formatters.Formatter`:

```python
# mypackage/formatters/custom.py
from dbt_score.formatters import Formatter
from dbt_score.models import Evaluable
from dbt_score.scoring import Score


class MyCustomFormatter(Formatter):
    def evaluable_evaluated(self, evaluable: Evaluable, results, score: Score) -> None:
        # Called after each model/source/etc is evaluated
        print(f"{evaluable.name}: {score.value:.1f}")

    def project_evaluated(self, score: Score) -> None:
        # Called after the entire project is evaluated
        print(f"Project score: {score.value:.1f}")
```

### Using a custom formatter

Specify the formatter using its fully qualified name:

```shell
dbt-score lint --format mypackage.formatters.custom.MyCustomFormatter
```

See the [Formatter reference](reference/formatters/index.md) for all available
methods to override.

## Exit codes

When `dbt-score` terminates, it exists with one of the following exit codes:

- `0` in case of successful termination. This is the happy case, when the
  project being linted either doesn't raise any warning, or the warnings are
  small enough to be above the thresholds. This generally means "successful
  linting".
- `1` in case of linting errors. This is the unhappy case: some entities in the
  project raise enough warnings to have a score below the defined thresholds.
  This generally means "linting doesn't pass".
- `2` in case of an unexpected error. This happens for example if something is
  misconfigured (for example a faulty dbt project), or the wrong parameters are
  given to the CLI. This generally means "setup needs to be fixed".
