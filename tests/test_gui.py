import pytest
import sys
import os
import types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import gui

class DummyWorkout:
    def __init__(self, date, duration=30, total_weight_lifted=100, total_reps_performed=50, number_of_exercises=2, number_of_exercise_sets=4, exercises=None):
        self.date = date
        self.duration = duration
        self.total_weight_lifted = total_weight_lifted
        self.total_reps_performed = total_reps_performed
        self.number_of_exercises = number_of_exercises
        self.number_of_exercise_sets = number_of_exercise_sets
        self.exercises = exercises or []

def test_load_workouts_file_not_found(monkeypatch):
    """Test: load_workouts returns [] if file does not exist."""
    monkeypatch.setattr(sys, 'argv', ['prog', '/tmp/nonexistent.csv'])
    assert gui.load_workouts() == []

def test_load_workouts_parse_error(monkeypatch):
    """Test: load_workouts returns [] if parse_csv raises an exception."""
    def bad_parse_csv(path):
        raise Exception('parse error')
    monkeypatch.setattr(sys, 'argv', ['prog', '/tmp/fake.csv'])
    monkeypatch.setattr(os.path, 'isfile', lambda p: True)
    monkeypatch.setattr(gui, 'parse_csv', bad_parse_csv)
    assert gui.load_workouts() == []

def test_filter_workouts_date_range():
    """Test: filter_workouts returns only workouts within the given date range."""
    from datetime import datetime, timedelta
    d1 = DummyWorkout(datetime(2024, 1, 1))
    d2 = DummyWorkout(datetime(2024, 1, 10))
    d3 = DummyWorkout(datetime(2024, 2, 1))
    workouts = [d1, d2, d3]
    start = datetime(2024, 1, 5).date()
    end = datetime(2024, 1, 31).date()
    filtered = gui.filter_workouts(workouts, [start, end])
    assert d2 in filtered and d1 not in filtered and d3 not in filtered

def test_filter_workouts_no_range():
    """Test: filter_workouts returns all workouts if no date range is given."""
    workouts = [DummyWorkout(1), DummyWorkout(2)]
    assert gui.filter_workouts(workouts, []) == workouts

def test_upload_page_shown_when_no_data(monkeypatch):
    """Test: Upload Data page is shown when no workouts are loaded."""
    import streamlit as st
    # Patch session_state to simulate no workouts
    monkeypatch.setattr(st, 'session_state', {})
    # Patch load_workouts to return []
    monkeypatch.setattr(gui, 'load_workouts', lambda: [])
    # Patch sidebar.selectbox to capture options
    called = {}
    def fake_selectbox(label, options, index=0):
        called['options'] = options
        return options[index]
    monkeypatch.setattr(gui.st.sidebar, 'selectbox', fake_selectbox)
    # Patch st.write to capture output
    output = {}
    monkeypatch.setattr(gui.st, 'write', lambda msg: output.setdefault('write', []).append(msg))
    # Patch st.title to avoid actual UI
    monkeypatch.setattr(gui.st, 'title', lambda msg: None)
    # Patch st.date_input to avoid UI
    monkeypatch.setattr(gui.st, 'date_input', lambda *a, **k: [None, None])
    # Patch st.button to always False
    monkeypatch.setattr(gui.st, 'button', lambda *a, **k: False)
    # Patch st.file_uploader to None
    monkeypatch.setattr(gui.st, 'file_uploader', lambda *a, **k: None)
    # Patch st.text_input to empty
    monkeypatch.setattr(gui.st, 'text_input', lambda *a, **k: '')
    # Patch st.spinner to context manager
    class DummySpinner:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): return False
    monkeypatch.setattr(gui.st, 'spinner', lambda *a, **k: DummySpinner())
    # Patch st.success, st.error, st.info
    monkeypatch.setattr(gui.st, 'success', lambda *a, **k: None)
    monkeypatch.setattr(gui.st, 'error', lambda *a, **k: None)
    monkeypatch.setattr(gui.st, 'info', lambda *a, **k: None)
    # Run main
    gui.main()
    assert 'Upload Data' in called['options']


def test_upload_page_handles_non_csv(monkeypatch):
    """Test: Upload Data page handles non-CSV uploads gracefully (no crash)."""
    import streamlit as st
    monkeypatch.setattr(st, 'session_state', {})
    monkeypatch.setattr(gui, 'load_workouts', lambda: [])
    monkeypatch.setattr(gui.st.sidebar, 'selectbox', lambda *a, **k: 'Upload Data')
    monkeypatch.setattr(gui.st, 'title', lambda msg: None)
    monkeypatch.setattr(gui.st, 'write', lambda msg: None)
    monkeypatch.setattr(gui.st, 'date_input', lambda *a, **k: [None, None])
    monkeypatch.setattr(gui.st, 'button', lambda *a, **k: True)
    monkeypatch.setattr(gui.st, 'file_uploader', lambda *a, **k: types.SimpleNamespace(read=lambda: b'not a csv'))
    monkeypatch.setattr(gui.st, 'text_input', lambda *a, **k: '')
    class DummySpinner:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): return False
    monkeypatch.setattr(gui.st, 'spinner', lambda *a, **k: DummySpinner())
    monkeypatch.setattr(gui.st, 'success', lambda *a, **k: None)
    monkeypatch.setattr(gui.st, 'error', lambda *a, **k: None)
    monkeypatch.setattr(gui.st, 'info', lambda *a, **k: None)
    # Patch parse_csv to raise Exception for non-CSV
    monkeypatch.setattr(gui, 'parse_csv', lambda path: (_ for _ in ()).throw(Exception('bad csv')))
    # Patch os.remove to avoid file errors
    monkeypatch.setattr(os, 'remove', lambda *a, **k: None)
    # Should not raise
    gui.main()


def test_all_pages_display(monkeypatch):
    """Test: All pages (Home, Graphs, Upload Data) display without error when workouts exist."""
    import streamlit as st
    from datetime import datetime
    dummy = DummyWorkout(datetime(2024, 1, 1))
    monkeypatch.setattr(st, 'session_state', {'workouts': [dummy]})
    monkeypatch.setattr(gui.st.sidebar, 'selectbox', lambda *a, **k: 'Home')
    monkeypatch.setattr(gui.st, 'title', lambda msg: None)
    monkeypatch.setattr(gui.st, 'write', lambda msg: None)
    monkeypatch.setattr(gui.st, 'date_input', lambda *a, **k: [dummy.date.date(), dummy.date.date()])
    monkeypatch.setattr(gui.st, 'button', lambda *a, **k: False)
    monkeypatch.setattr(gui.st, 'metric', lambda *a, **k: None)
    # Home page
    gui.main()
    # Graphs page
    monkeypatch.setattr(gui.st.sidebar, 'selectbox', lambda *a, **k: 'Graphs')
    monkeypatch.setattr(gui.st, 'line_chart', lambda *a, **k: None)
    monkeypatch.setattr(gui.st, 'altair_chart', lambda *a, **k: None)
    gui.main()
    # Upload Data page
    monkeypatch.setattr(gui.st.sidebar, 'selectbox', lambda *a, **k: 'Upload Data')
    monkeypatch.setattr(gui.st, 'file_uploader', lambda *a, **k: None)
    monkeypatch.setattr(gui.st, 'text_input', lambda *a, **k: '')
    gui.main()
