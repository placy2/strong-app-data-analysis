"""Tests for the pure parsing helpers in utils.parse_utils."""
import pytest

from utils.parse_utils import (
    load_mappings,
    parse_duration,
    parse_set_order,
    parse_to_int,
)


@pytest.mark.parametrize(
    "duration_str, expected",
    [
        ("53m", 53),
        ("1h 31m", 91),
        ("32h 5m", 1925),
        ("2h", 120),
    ],
)
def test_parse_duration(duration_str, expected):
    assert parse_duration(duration_str) == expected


@pytest.mark.parametrize("set_order, expected", [("1", 1), ("12", 12), ("0", 0)])
def test_parse_set_order_numeric(set_order, expected):
    assert parse_set_order(set_order) == expected


@pytest.mark.parametrize("special", ["W", "F", "D"])
def test_parse_set_order_special_cases_are_zero(special):
    assert parse_set_order(special) == 0


def test_parse_set_order_invalid_raises():
    with pytest.raises(ValueError):
        parse_set_order("X")


@pytest.mark.parametrize(
    "value, expected",
    [("0", 0), ("0.0", 0), ("42", 42), ("12.9", 12), ("junk", 0), ("", 0)],
)
def test_parse_to_int(value, expected):
    assert parse_to_int(value) == expected


def test_load_mappings_reads_existing_file(tmp_path):
    mapping_file = tmp_path / "mappings.json"
    mapping_file.write_text('{"Bench Press": "Pecs"}', encoding="utf-8")
    assert load_mappings(str(mapping_file)) == {"Bench Press": "Pecs"}


def test_load_mappings_missing_file_returns_empty(tmp_path):
    assert load_mappings(str(tmp_path / "does_not_exist.json")) == {}
