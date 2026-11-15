import pytest
from unittest.mock import patch, MagicMock
from backend.app.tools.unified_computer_controller import unified_controller


def test_mouse_cursor_and_movement():
    """Verify Win32 mouse cursor coordinates and movement."""
    pos = unified_controller.get_cursor_position()
    assert "x" in pos
    assert "y" in pos
    assert isinstance(pos["x"], int)
    assert isinstance(pos["y"], int)

    # Test mouse move with valid coordinates
    moved = unified_controller.mouse_move(pos["x"], pos["y"])
    assert moved is True


def test_mouse_click_and_scroll():
    """Verify Win32 mouse clicking and scrolling."""
    # Test left, right, double click
    with patch.object(unified_controller._user32, "mouse_event") as mock_me:
        assert unified_controller.mouse_click(button="left", clicks=1) is True
        assert mock_me.call_count == 2  # down + up

        mock_me.reset_mock()
        assert unified_controller.mouse_click(button="right", clicks=1) is True
        assert mock_me.call_count == 2

        mock_me.reset_mock()
        assert unified_controller.mouse_click(clicks=2) is True
        assert mock_me.call_count == 4  # (down + up) * 2

        mock_me.reset_mock()
        assert unified_controller.mouse_scroll(-240) is True
        assert mock_me.call_count == 1


def test_keyboard_key_presses():
    """Verify virtual keyboard key presses for enter, space, esc, tab."""
    with patch.object(unified_controller, "send_virtual_key", return_value=True) as mock_vk:
        assert unified_controller.press_key("enter") is True
        assert mock_vk.call_count == 2  # down + up

        mock_vk.reset_mock()
        assert unified_controller.press_key("space") is True
        assert mock_vk.call_count == 2

        mock_vk.reset_mock()
        assert unified_controller.press_key("esc") is True
        assert mock_vk.call_count == 2


def test_compound_web_search_with_fillers():
    """Verify 'hey Google open Chrome and search about internet' resolves directly to Chrome search."""
    with patch.object(unified_controller, "web_search", return_value={"success": True, "message": "Searching Google for 'internet', Sir."}) as mock_ws:
        res = unified_controller.execute_directive("hey Google open Chrome and search about internet")
        assert res is not None
        assert res.get("success") is True
        assert "internet" in res.get("message", "").lower()
        mock_ws.assert_called_once()
        args, kwargs = mock_ws.call_args
        assert "internet" in args[0].lower()
        assert kwargs.get("engine") == "google"


def test_compound_youtube_song_with_stutters():
    """Verify 'can you can you can you open Chrome and then open YouTube and play some song'."""
    with patch.object(unified_controller, "web_search", return_value={"success": True, "message": "Playing on YouTube, Sir."}) as mock_ws:
        res = unified_controller.execute_directive("can you can you can you can you can you open Chrome and then open YouTube and play some song")
        assert res is not None
        assert res.get("success") is True
        mock_ws.assert_called_once()
        args, kwargs = mock_ws.call_args
        assert kwargs.get("engine") == "youtube"


def test_human_typing_directive():
    """Verify 'type hello world' executes unicode typing."""
    with patch.object(unified_controller, "type_unicode_text", return_value=True) as mock_tut:
        res = unified_controller.execute_directive("type hello world")
        assert res is not None
        assert res.get("success") is True
        mock_tut.assert_called_once_with("hello world")


def test_mouse_directive_parsing():
    """Verify natural click and scroll commands."""
    with patch.object(unified_controller, "mouse_click", return_value=True) as mock_mc:
        res = unified_controller.execute_directive("double click")
        assert res is not None
        mock_mc.assert_called_once_with(clicks=2)

    with patch.object(unified_controller, "mouse_scroll", return_value=True) as mock_ms:
        res = unified_controller.execute_directive("scroll down")
        assert res is not None
        mock_ms.assert_called_once_with(-240)
