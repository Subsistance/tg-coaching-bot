import pytest
from unittest.mock import AsyncMock
from bot import handle_answer, user_data, QUESTION, RESULT

@pytest.mark.asyncio
async def test_handle_answer_progress():
    user_id = 5678
    user_data[user_id] = {"score": 0, "index": 0}

    mock_update = AsyncMock()
    mock_update.effective_chat.id = user_id
    mock_update.message.text = "Чувствую, что похвала заслуженная"

    mock_context = AsyncMock()

    next_state = await handle_answer(mock_update, mock_context)
    assert user_data[user_id]["score"] > 0
    assert next_state in [QUESTION, RESULT]