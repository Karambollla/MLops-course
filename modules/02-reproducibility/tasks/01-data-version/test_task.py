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


@pytest.mark.parametrize("chunk", [1, 7, 255, 65536, 100000])
def test_binary_hash_across_chunk_boundaries(tmp_path, chunk):
    data = bytes(range(256)) * 300 + b"\x00\xff\r\n"
    path = tmp_path / "binary"
    path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    assert s.sha256_file(path, chunk) == digest
    assert s.verify_restore(digest, path) is None
    assert path.read_bytes() == data
    changed = data[:-1] + b"X"
    path.write_bytes(changed)
    assert s.sha256_file(path, chunk) == hashlib.sha256(changed).hexdigest()
    with pytest.raises(ValueError):
        s.verify_restore(digest, path)
    assert path.read_bytes() == changed


def test_negative_chunk_and_missing_restore(tmp_path):
    path = tmp_path / "data"
    path.write_bytes(b"abc")
    with pytest.raises(ValueError):
        s.sha256_file(path, -1)
    with pytest.raises(Exception) as failure:
        s.verify_restore(hashlib.sha256(b"abc").hexdigest(), tmp_path / "missing")
    assert not isinstance(failure.value, NotImplementedError)
