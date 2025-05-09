import csv
import io
import asyncio
import tempfile
import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest import mock
from unittest.mock import patch
from bot import log_user_action, update_signup_record, CSV_COLUMNS

class UnclosableStringIO(io.StringIO):
    def close(self):
        pass  # override close to do nothing

# === Tests for log_user_action ===

def test_log_user_action():
    # Create a fake file-like object using io.StringIO
    fake_file = UnclosableStringIO()

    # Patch 'open' to return our fake file instead of opening a real file
    with mock.patch("builtins.open", return_value=fake_file), \
         mock.patch("os.path.exists", return_value=False):

        # Call the function you're testing
        log_user_action(123, "TestUser", "TestAction", "Extra info")

        # Now read from fake file (still open)
        fake_file.seek(0)
        lines = fake_file.readlines()

    assert len(lines) == 2  # One for header, one for the entry
    assert "TestUser" in lines[1]
    assert "TestAction" in lines[1]


# === Tests for update_signup_record ===

@pytest.mark.asyncio
async def test_update_signup_record_adds_user():
    # Create temp file and immediately close it so it can be reused
    fd, temp_filename = tempfile.mkstemp(suffix=".csv")
    os.close(fd)  # ✅ close immediately

    try:
        await update_signup_record(
            user_id="123",
            username="Test User",
            phone="1234567890",
            score="20",
            source="instagram",
            last_step="Started test",
            status="pending",
            filename=temp_filename
        )

        with open(temp_filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["Username"] == "Test User"
        assert rows[0]["Phone"] == "1234567890"
        assert rows[0]["Source"] == "instagram"
        assert rows[0]["Score"] == "20"

    finally:
        os.remove(temp_filename)