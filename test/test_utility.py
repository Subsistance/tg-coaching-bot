import pytest
from bot import escape_markdown_v2

def test_escape_markdown_v2_preserves_formatting():
    raw = "Это *жирный*, _курсив_, `код`, ~зачёркнутый~"
    result = escape_markdown_v2(raw)

    # Should preserve formatting characters
    assert "*жирный*" in result
    assert "_курсив_" in result
    assert "`код`" in result
    assert "~зачёркнутый~" in result

def test_escape_markdown_v2_escapes_special_chars():
    raw = "Символы: [ ] ( ) { } . ! > # + - = |"
    result = escape_markdown_v2(raw)

    # All special chars should be escaped with backslash
    for char in r"[](){}.!>#+-=|":
        assert f"\\{char}" in result