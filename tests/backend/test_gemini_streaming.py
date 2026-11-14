"""
Unit Tests for Non-Blocking Streaming Gemini Provider in JARVIS Mark XI:
- Verifies async queue bridge yields delta chunks and completed sentinel
- Verifies graceful error handling and fallback candidate iteration
"""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import MagicMock, patch

from backend.app.ai.gemini_provider import gemini_provider


@pytest.mark.asyncio
async def test_stream_chat_mocked_success():
    """Verify non-blocking queue stream yields deltas and completes."""
    mock_chunk1 = MagicMock()
    mock_chunk1.text = "Hello "
    mock_chunk2 = MagicMock()
    mock_chunk2.text = "Sir."

    mock_client = MagicMock()
    mock_client.models.generate_content_stream.return_value = [mock_chunk1, mock_chunk2]

    with patch.object(gemini_provider, "_get_client", return_value=mock_client):
        chunks: list[dict] = []
        async for chunk in gemini_provider.stream_chat(
            message="Test prompt",
            system_instruction="Test system",
            model="gemini-3.8-flash",
        ):
            chunks.append(chunk)

        delta_texts = [c["text"] for c in chunks if c.get("type") == "delta"]
        assert "".join(delta_texts) == "Hello Sir."

        completed_chunks = [c for c in chunks if c.get("type") == "completed"]
        assert len(completed_chunks) == 1
        assert completed_chunks[0]["model"] == "gemini-3.8-flash"


@pytest.mark.asyncio
async def test_stream_chat_fallback_on_error():
    """Verify stream falls back to secondary models if primary model fails."""
    mock_client = MagicMock()
    
    def fail_first(model, contents, config):
        if "3.8-flash" in model:
            raise RuntimeError("API quota exceeded")
        mock_c = MagicMock()
        mock_c.text = "Fallback response"
        return [mock_c]

    mock_client.models.generate_content_stream.side_effect = fail_first

    with patch.object(gemini_provider, "_get_client", return_value=mock_client):
        chunks: list[dict] = []
        async for chunk in gemini_provider.stream_chat(
            message="Fallback test",
            system_instruction="Test system",
            model="gemini-3.8-flash",
        ):
            chunks.append(chunk)

        delta_texts = [c["text"] for c in chunks if c.get("type") == "delta"]
        assert "Fallback response" in delta_texts
        completed_chunks = [c for c in chunks if c.get("type") == "completed"]
        assert len(completed_chunks) == 1
