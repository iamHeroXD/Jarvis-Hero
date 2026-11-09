"""Integration tests for Projects, Automations, Activity, and System APIs."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.database.session import init_db
from backend.app.security.auth import hash_password, create_access_token
from backend.app.models.database_models import User
from backend.app.database.session import get_session


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_test_db():
    await init_db()
    async with get_session() as session:
        # Create test owner user if not present
        from sqlalchemy import select
        stmt = select(User).where(User.username == "test_owner")
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            user = User(
                username="test_owner",
                display_name="Test Owner",
                hashed_password=hash_password("test_pass_123"),
                is_owner=True,
                is_active=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)


@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "1", "username": "test_owner", "is_owner": True})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_projects_lifecycle_and_git_status(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. List projects - should auto-seed RCN and Clearly AI
        res = await ac.get("/api/v1/projects", headers=auth_headers)
        assert res.status_code == 200
        projects = res.json()
        assert len(projects) >= 2
        names = [p["name"] for p in projects]
        assert any("RCN" in n for n in names)
        assert any("Clearly AI" in n for n in names)

        rcn_proj = next(p for p in projects if "RCN" in p["name"])

        # 2. Check Git status on RCN project
        git_res = await ac.get(f"/api/v1/projects/{rcn_proj['id']}/git-status", headers=auth_headers)
        assert git_res.status_code == 200
        git_data = git_res.json()
        assert git_data["is_git"] is True
        assert "branch" in git_data

        # 3. Add Project Note
        note_res = await ac.post(
            f"/api/v1/projects/{rcn_proj['id']}/notes",
            headers=auth_headers,
            json={"content": "Completed Phase 5/6/7 master command integration.", "note_type": "milestone"},
        )
        assert note_res.status_code == 201
        note_data = note_res.json()
        assert note_data["note_type"] == "milestone"

        # 4. List Notes
        notes_list = await ac.get(f"/api/v1/projects/{rcn_proj['id']}/notes", headers=auth_headers)
        assert notes_list.status_code == 200
        assert len(notes_list.json()) >= 1


@pytest.mark.asyncio
async def test_automations_lifecycle(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. List automations - should seed defaults
        res = await ac.get("/api/v1/automations", headers=auth_headers)
        assert res.status_code == 200
        autos = res.json()
        assert len(autos) >= 3
        auto = autos[0]

        # 2. Trigger run now
        run_res = await ac.post(f"/api/v1/automations/{auto['id']}/run", headers=auth_headers)
        assert run_res.status_code == 200
        run_data = run_res.json()
        assert run_data["status"] == "success"
        assert len(run_data["details"]) >= 1

        # 3. Toggle automation
        toggle_res = await ac.patch(f"/api/v1/automations/{auto['id']}/toggle", headers=auth_headers)
        assert toggle_res.status_code == 200
        assert toggle_res.json()["is_enabled"] != auto["is_enabled"]


@pytest.mark.asyncio
async def test_activity_log(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/activity?limit=10", headers=auth_headers)
        assert res.status_code == 200
        logs = res.json()
        assert len(logs) >= 1
        assert "action" in logs[0]
        assert "result" in logs[0]


@pytest.mark.asyncio
async def test_system_and_governor(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # System metrics
        met_res = await ac.get("/api/v1/system/metrics", headers=auth_headers)
        assert met_res.status_code == 200
        assert "cpu_percent" in met_res.json()

        # Governor status
        gov_res = await ac.get("/api/v1/governor/status", headers=auth_headers)
        assert gov_res.status_code == 200
        assert "target_particle_count" in gov_res.json()

        # Governor set profile
        set_gov = await ac.post(
            "/api/v1/governor/set-profile",
            headers=auth_headers,
            json={"profile": "eco"},
        )
        assert set_gov.status_code == 200
        assert set_gov.json()["state"]["profile"] == "eco"
        assert set_gov.json()["state"]["target_particle_count"] == 600
