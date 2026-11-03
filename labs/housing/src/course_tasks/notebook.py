"""Import marked definitions from a trusted notebook, without running its lab."""

import json
from pathlib import Path
from types import ModuleType

from course_tasks import course_root


def housing_notebook_path() -> Path:
    modules = (course_root() / "modules").resolve()
    directory = (modules / "01-ml").resolve()
    path = (directory / "housing.ipynb").resolve()
    if not directory.is_relative_to(modules) or not path.is_relative_to(directory):
        raise ValueError("Notebook должен находиться внутри modules/01-ml")
    return path


def load_notebook(path: Path) -> ModuleType:
    """Read saved Python definitions afresh; this is not a code sandbox."""
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Некорректный notebook {path}: {error}") from error
    if (
        not isinstance(notebook, dict)
        or notebook.get("nbformat") != 4
        or not isinstance(notebook.get("cells"), list)
    ):
        raise ValueError(f"Ожидается notebook формата 4: {path}")
    required = {"course:imports", "course:definitions"}
    selected = []
    found = set()
    for number, cell in enumerate(notebook["cells"], start=1):
        if not isinstance(cell, dict) or cell.get("cell_type") != "code":
            continue
        tags = cell.get("metadata", {}).get("tags", [])
        matching = required.intersection(tags)
        if not matching:
            continue
        found.update(matching)
        source = cell.get("source", "")
        if isinstance(source, list):
            source = "".join(source)
        selected.append(compile(source, f"{path}::cell-{number}", "exec"))
    if missing := required - found:
        raise ValueError(f"Нет ячеек {', '.join(sorted(missing))}: {path}")
    module = ModuleType("housing_notebook")
    module.__file__ = str(path)
    for code in selected:
        exec(code, module.__dict__)
    return module
