import pytest
from scrivener_assistant.rtf_converter import convert_rtf_to_text

def test_convert_plain():
    rtf = r"{\rtf1\ansi Hello World}"
    assert convert_rtf_to_text(rtf).strip() == "Hello World"

def test_convert_bold_italic():
    rtf = r"{\rtf1\ansi \b Bold \b0 and \i Italic \i0}"
    text = convert_rtf_to_text(rtf).strip()
    assert "Bold and Italic" == text

def test_convert_newlines_par():
    rtf = r"{\rtf1\ansi Line 1\par Line 2}"
    text = convert_rtf_to_text(rtf)
    assert "Line 1" in text
    assert "Line 2" in text
