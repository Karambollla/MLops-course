"""Copy declared artifacts without importing or executing student solutions."""

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from contextlib import ExitStack
from pathlib import Path


def _digest(path: Path) -> bytes:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").digest()


def _invalid_constant(value: str):
    raise ValueError(f"Недопустимая JSON-константа: {value}")


def export_files(
    files: list[tuple[Path, Path]], *, replace: bool = False
) -> list[Path]:
    """Validate everything first, stage copies, then replace files in given order.

    Callers declare metadata before the model. Each replacement is atomic;
    the whole set is not a transaction. Identical files remain untouched.
    """
    for source, _ in files:
        if not source.is_file():
            raise FileNotFoundError(f"Нет файла результата: {source}")
        if source.stat().st_size == 0:
            raise ValueError(f"Пустой файл результата: {source}")
        if source.suffix == ".json":
            try:
                json.loads(
                    source.read_text(encoding="utf-8"), parse_constant=_invalid_constant
                )
            except ValueError as error:
                raise ValueError(f"Некорректный JSON: {source}: {error}") from error

    pending = []
    conflicts = []
    for source, target in files:
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError(f"Назначение должно быть обычным файлом: {target}")
        if target.exists():
            if _digest(source) == _digest(target):
                continue
            conflicts.append(target)
        pending.append((source, target))
    if conflicts and not replace:
        paths = "\n".join(str(path) for path in conflicts)
        raise FileExistsError(
            f"Уже существуют другие результаты:\n{paths}\nДля замены добавь --replace."
        )

    with ExitStack() as cleanup:
        staged = []
        for source, target in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary = Path(stream.name)
            cleanup.callback(temporary.unlink, missing_ok=True)
            shutil.copy2(source, temporary)
            staged.append((temporary, target))
        for temporary, target in staged:
            os.replace(temporary, target)
    return [target for _, target in pending]


def export_cli(files: list[tuple[Path, Path]], *, service: str) -> None:
    parser = argparse.ArgumentParser(
        description="Перенос готовых файлов задания в work/. Решение не запускается."
    )
    parser.add_argument(
        "--replace", action="store_true", help="Заменить отличающиеся результаты"
    )
    args = parser.parse_args()
    try:
        changed = export_files(files, replace=args.replace)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if changed:
        for path in changed:
            print(f"Перенесён: {path}")
        print(f"После замены модели перезапусти {service}.")
    else:
        print("Все файлы уже совпадают; изменений нет.")
