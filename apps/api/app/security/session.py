"""
Session management using Redis.

Per project rules:
- Logout must invalidate session server-side.
- Session expiry must be enforced.
- Do not store secrets in localStorage.
- Sessions use httpOnly secure cookies.
"""

import json
import secrets
import uuid
from datetime import UTC, datetime
from typing import Any

from app.config import settings

SESSION_TTL_SECONDS = 86400  # 24 hours
SESSION_PREFIX = "session:"

# In-memory session store (development only fallback)
_MEMORY_SESSIONS: dict[str, dict[str, Any]] = {}


def generate_session_token() -> str:
    """Generate a cryptographically secure session token."""
    return secrets.token_urlsafe(48)


async def create_session(
    user_id: uuid.UUID,
    role: str,
    identifier: str,
    display_name: str,
) -> str:
    """Create a new session in memory."""
    token = generate_session_token()
    session_data = {
        "user_id": str(user_id),
        "role": role,
        "identifier": identifier,
        "display_name": display_name,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _MEMORY_SESSIONS[token] = session_data
    return token


async def get_session(token: str) -> dict[str, str] | None:
    """Retrieve session data from memory."""
    return _MEMORY_SESSIONS.get(token)


async def refresh_session(token: str) -> bool:
    """Extend a session's TTL (no-op in memory)."""
    return token in _MEMORY_SESSIONS


async def delete_session(token: str) -> None:
    """Invalidate a session by removing it from memory."""
    _MEMORY_SESSIONS.pop(token, None)


async def delete_all_user_sessions(user_id: uuid.UUID) -> int:
    """Delete all sessions for a given user."""
    deleted = 0
    tokens_to_delete = []
    for token, data in _MEMORY_SESSIONS.items():
        if data.get("user_id") == str(user_id):
            tokens_to_delete.append(token)
            deleted += 1
            
    for token in tokens_to_delete:
        _MEMORY_SESSIONS.pop(token, None)
        
    return deleted
