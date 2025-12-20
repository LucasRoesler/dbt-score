"""Custom test formatter for testing formatter registry discovery."""

from dbt_score.formatters import Formatter
from dbt_score.models import Evaluable
from dbt_score.scoring import Score


class CustomTestFormatter(Formatter):
    """A custom formatter for testing."""

    def evaluable_evaluated(
        self, evaluable: Evaluable, results: dict, score: Score
    ) -> None:
        """Callback when an evaluable item has been evaluated."""
        pass

    def project_evaluated(self, score: Score) -> None:
        """Callback when a project has been evaluated."""
        pass
