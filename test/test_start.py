import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import AsyncMock, Mock, patch
from bot import start, WELCOME

@pytest.mark.asyncio
async def test_start_command():
    mock_update = AsyncMock()
    mock_update.effective_user.id = 1234
    mock_update.effective_user.full_name = "Test User"
    mock_update.message = AsyncMock()
    mock_update.message.text = "/start instagram"
    mock_update.callback_query = None

    mock_context = AsyncMock()
    mock_context.args = ["instagram"]

    # ✅ Patch both log_user_action (sync) and update_signup_record (async)
    with patch("bot.update_signup_record", new_callable=AsyncMock), \
            patch("bot.log_user_action", new_callable=Mock):
        result = await start(mock_update, mock_context)

        # ✅ Verify message was sent
        mock_update.message.reply_text.assert_called_once()
        assert result == WELCOME