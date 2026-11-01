"""Учебная заготовка. Контракт: README.md рядом с файлом."""

# ruff: noqa: F401
# Импорты подготовлены для самостоятельной реализации задания.

import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path


def recover_registration(pending: dict, register, local_path: Path) -> dict:
    # TODO: durable pending, retry исходного run, запрет автопродвижения.
    raise NotImplementedError("Восстанови регистрацию")
