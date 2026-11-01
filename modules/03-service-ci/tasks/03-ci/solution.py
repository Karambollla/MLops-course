"""Необязательный read-only сбор CI истории; основной starter ci-runs.json."""


def collect_ci_runs(repository: str, branch: str) -> list[dict]:
    # TODO: получить GitHub Actions runs/jobs через HTTP API (lazy urllib),
    # вернуть sha/branch/conclusion/url/passed_checks; не запускать workflow,
    # не публиковать образы, не создавать секреты. Допустим ручной экспорт.
    raise NotImplementedError("Собери реальные CI run IDs и результаты")
