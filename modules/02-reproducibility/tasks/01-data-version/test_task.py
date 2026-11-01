"""Offline проверки поведения; исходная заготовка должна быть RED."""

import hashlib

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_hash_and_restore(tmp_path):
    p = tmp_path / "data.csv"
    p.write_bytes(b"x,y\n1,2\n")
    expected = hashlib.sha256(p.read_bytes()).hexdigest()
    assert s.sha256_file(p, 3) == expected
    assert s.verify_restore(expected, p) is None
    p.write_bytes(b"x,y\n1,3\n")
    with pytest.raises(ValueError):
        s.verify_restore(expected, p)


def test_hash_empty_and_bad_chunk(tmp_path):
    p = tmp_path / "empty"
    p.touch()
    assert s.sha256_file(p) == hashlib.sha256(b"").hexdigest()
    with pytest.raises(ValueError):
        s.sha256_file(p, 0)
    with pytest.raises(FileNotFoundError):
        s.sha256_file(tmp_path / "absent")
