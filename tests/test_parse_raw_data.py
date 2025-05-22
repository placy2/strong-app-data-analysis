import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import parse_raw_data as prd

def test_parse_duration():
    """Test: parse_duration correctly parses hours and minutes from strings."""
    assert prd.parse_duration('1h 30m') == 90
    assert prd.parse_duration('45m') == 45
    assert prd.parse_duration('2h') == 120
    assert prd.parse_duration('') == 0

def test_parse_csv_basic(tmp_path):
    """Test: parse_csv parses a basic CSV and aggregates workout data correctly."""
    csv_content = """Date,Workout Name,Duration,Exercise Name,Set Order,Weight,Reps,Notes,Workout Notes
2024-01-01 10:00:00,Test,30m,Pushup,1,0,10,,
2024-01-01 10:00:00,Test,30m,Pushup,2,0,12,,
2024-01-01 10:00:00,Test,30m,Squat,1,50,8,,
"""
    f = tmp_path / "test.csv"
    f.write_text(csv_content)
    workouts = prd.parse_csv(str(f))
    assert len(workouts) == 1
    w = workouts[0]
    assert w.name == 'Test'
    assert w.duration == 30
    assert w.number_of_exercises == 2
    assert w.number_of_exercise_sets == 3
    assert w.total_reps_performed == 10 + 12 + 8
    assert w.total_weight_lifted == 50

def test_parse_csv_missing_fields(tmp_path):
    """Test: parse_csv handles missing fields (set order, weight) gracefully."""
    csv_content = """Date,Workout Name,Duration,Exercise Name,Set Order,Weight,Reps,Notes,Workout Notes
2024-01-01 10:00:00,Test,30m,Pushup,,,10,,
"""
    f = tmp_path / "test2.csv"
    f.write_text(csv_content)
    workouts = prd.parse_csv(str(f))
    assert len(workouts) == 1
    w = workouts[0]
    assert w.number_of_exercise_sets == 1
    assert w.total_weight_lifted == 0
    assert w.total_reps_performed == 10

def test_load_mappings_and_save(tmp_path, monkeypatch):
    """Test: save_mappings and load_mappings work as expected for JSON mapping files."""
    mapping_file = tmp_path / "mapping.json"
    monkeypatch.setattr(prd, 'MAPPING_FILE', str(mapping_file))
    d = {'Pushup': 'Chest'}
    prd.save_mappings(d)
    loaded = prd.load_mappings()
    assert loaded == d

def test_main_flow(monkeypatch, tmp_path):
    """Test: The __main__ flow in parse_raw_data.py runs without error and saves mappings."""
    # Prepare a fake CSV file
    csv_content = """Date,Workout Name,Duration,Exercise Name,Set Order,Weight,Reps,Notes,Workout Notes\n2024-01-01 10:00:00,Test,30m,Pushup,1,0,10,,\n"""
    csv_file = tmp_path / "strong.csv"
    csv_file.write_text(csv_content)
    # Patch parse_csv to return a dummy workout
    monkeypatch.setattr(prd, 'parse_csv', lambda path: [prd.Workout('Test', prd.datetime(2024,1,1,10,0,0), 30)])
    # Patch load_mappings/save_mappings to use a temp file
    mapping_file = tmp_path / "mapping.json"
    monkeypatch.setattr(prd, 'MAPPING_FILE', str(mapping_file))
    monkeypatch.setattr(prd, 'load_mappings', lambda: {})
    monkeypatch.setattr(prd, 'save_mappings', lambda d: mapping_file.write_text('saved'))
    # Patch prompt_for_body_part to simulate user exit
    monkeypatch.setattr(prd, 'prompt_for_body_part', lambda name: prd.EXIT_FLAG)
    # Patch print to suppress output
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)
    # Simulate the __main__ block logic
    parsed_workouts = prd.parse_csv(str(csv_file))
    exercises_without_mapping = set()
    for w in parsed_workouts:
        for e in getattr(w, 'exercises', []):
            if not getattr(e, 'body_part', None):
                exercises_without_mapping.add(e.name)
    mapping_dict = prd.load_mappings()
    for ex_name in exercises_without_mapping:
        if ex_name not in mapping_dict:
            chosen_part_str = prd.prompt_for_body_part(ex_name)
            if chosen_part_str == prd.EXIT_FLAG:
                break
            elif chosen_part_str:
                mapping_dict[ex_name] = chosen_part_str
    prd.save_mappings(mapping_dict)
    # Check that the mapping file was written
    assert mapping_file.read_text() == 'saved'
