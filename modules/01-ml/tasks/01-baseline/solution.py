"""Учебная заготовка. Контракт: README.md рядом с файлом."""


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    # TODO: форма, конечность, MAE/RMSE.
    raise NotImplementedError("Реализуй метрики")


def make_split(n_rows: int, seed: int = 42) -> dict:
    # TODO: train_test_split в два этапа, исходные индексы.
    raise NotImplementedError("Разбей данные")


def fit_baseline(frame, split: dict) -> dict:
    # TODO: схема и DummyRegressor, без утечки test.
    raise NotImplementedError("Обучи baseline")
