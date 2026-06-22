import types
from unittest.mock import MagicMock

import scripts.gui as gui

def test_main_calls_navigation(monkeypatch):
    """Test that gui.main() initializes Streamlit navigation and runs navigation."""
    # Mock st and its methods
    fake_page = MagicMock()
    fake_navigation = MagicMock()
    fake_navigation.run = MagicMock()
    monkeypatch.setattr(gui, 'st', types.SimpleNamespace(
        Page=lambda *a, **k: fake_page,
        navigation=lambda pages: fake_navigation
    ))
    # Patch initialize_page to a no-op
    monkeypatch.setattr(gui, 'initialize_page', lambda: None)
    # Call main
    gui.main()
    # Check that navigation was called and run was called
    assert fake_navigation.run.called