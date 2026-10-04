"""
Tests for health and readiness endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_healthy(client: AsyncClient) -> None:
    """GET /health returns status 'healthy' with a timestamp."""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_response_format(client: AsyncClient) -> None:
    """GET /health returns the expected JSON structure."""
    response = await client.get("/health")
    data = response.json()
    assert isinstance(data["status"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["version"], str)
