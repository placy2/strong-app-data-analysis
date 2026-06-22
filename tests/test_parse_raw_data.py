"""Tests for the command-line mapping helpers in scripts.parse_raw_data."""
import json

from models import BodyPart
from scripts import parse_raw_data
from scripts.parse_raw_data import (
    EXIT_FLAG,
    main_flow,
    prompt_for_body_part,
    save_mappings,
)
from utils.parse_utils import load_mappings


def test_save_mappings_round_trips(tmp_path):
    mapping_file = tmp_path / "mappings.json"
    data = {"Bench Press": "Pecs", "Squat": "Quads"}
    save_mappings(data, str(mapping_file))

    assert json.loads(mapping_file.read_text(encoding="utf-8")) == data
    assert load_mappings(str(mapping_file)) == data


def test_prompt_for_body_part_valid_choice(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _="": "1")
    first_body_part = list(BodyPart)[0].value
    assert prompt_for_body_part("Shrug") == first_body_part


def test_prompt_for_body_part_quit_returns_exit_flag(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _="": "q")
    assert prompt_for_body_part("Shrug") == EXIT_FLAG


def test_prompt_for_body_part_non_digit_returns_none(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _="": "abc")
    assert prompt_for_body_part("Shrug") is None


def test_prompt_for_body_part_out_of_range_returns_none(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _="": "9999")
    assert prompt_for_body_part("Shrug") is None


def test_main_flow_quit_saves_no_mappings(monkeypatch, tmp_path, sample_csv):
    # No pre-existing mapping file, so every parsed exercise is prompted for.
    monkeypatch.setattr(parse_raw_data, "MAPPING_FILE", str(tmp_path / "missing.json"))
    monkeypatch.setattr("builtins.input", lambda _="": "q")
    out_file = tmp_path / "out.json"

    main_flow(file_path=sample_csv, mapping_file=str(out_file))

    assert json.loads(out_file.read_text(encoding="utf-8")) == {}


def test_main_flow_maps_every_exercise(monkeypatch, tmp_path, sample_csv):
    monkeypatch.setattr(parse_raw_data, "MAPPING_FILE", str(tmp_path / "missing.json"))
    monkeypatch.setattr("builtins.input", lambda _="": "1")
    out_file = tmp_path / "out.json"

    main_flow(file_path=sample_csv, mapping_file=str(out_file))

    saved = json.loads(out_file.read_text(encoding="utf-8"))
    first_body_part = list(BodyPart)[0].value
    assert set(saved) == {"Bench Press", "Bicep Curl", "Squat"}
    assert all(value == first_body_part for value in saved.values())
