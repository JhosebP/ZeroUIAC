from copy import deepcopy
import pytest
from fastapi.testclient import TestClient

from presentation.api import create_app


class FakeFacade:
    def __init__(self, *, fail=None):
        self.calls = []
        self.state = {"active": True}
        self.fail = fail
        self.status = {"active": True, "suspended": False, "voice_mode": "command"}
        self.session = {"session_active": False}
        self.adaptation = {"epsilon": 0.1, "q_states": 2}
        self.commands = {
            "modes": ["activar zoom"],
            "execution": ["enter"],
            "system": ["zero ui suspender"],
            "gestures": ["mover cabeza"],
        }

    def _call(self, name, value):
        self.calls.append(name)
        if self.fail == name:
            raise RuntimeError("C:\\private\\ZeroUI\\engine.py: hidden internal failure")
        return deepcopy(value)

    def get_system_status(self):
        return self._call("get_system_status", self.status)

    def get_session_metrics(self):
        return self._call("get_session_metrics", self.session)

    def get_adaptation_state(self):
        return self._call("get_adaptation_state", self.adaptation)

    def get_commands(self):
        return self._call("get_commands", self.commands)

    def suspend(self):
        self.state["active"] = False
        return self._call("suspend", {"success": True, "active": False, "suspended": True})

    def activate(self):
        self.state["active"] = True
        return self._call("activate", {"success": True, "active": True, "suspended": False})

    def show_commands(self):
        return self._call("show_commands", {"success": True, "commands_visible": True})

    def hide_commands(self):
        return self._call("hide_commands", {"success": True, "commands_visible": False})


@pytest.fixture
def facade():
    return FakeFacade()


@pytest.fixture
def client(facade):
    return TestClient(create_app(facade))


def test_health_check_is_static_and_does_not_call_facade(client, facade):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "zeroui-ac"}
    assert facade.calls == []


@pytest.mark.parametrize(
    ("path", "method", "expected"),
    [
        ("/api/status", "get_system_status", "status"),
        ("/api/session", "get_session_metrics", "session"),
        ("/api/adaptation", "get_adaptation_state", "adaptation"),
        ("/api/commands", "get_commands", "commands"),
        ("/api/system/suspend", "suspend", None),
        ("/api/system/activate", "activate", None),
        ("/api/commands/show", "show_commands", None),
        ("/api/commands/hide", "hide_commands", None),
    ],
)
def test_routes_delegate_once_and_preserve_facade_json(client, facade, path, method, expected):
    response = client.get(path) if method.startswith("get_") else client.post(path)
    assert response.status_code == 200
    assert facade.calls == [method]
    if expected:
        assert response.json() == getattr(facade, expected)
    else:
        control_results = {
            "suspend": {"success": True, "active": False, "suspended": True},
            "activate": {"success": True, "active": True, "suspended": False},
            "show_commands": {"success": True, "commands_visible": True},
            "hide_commands": {"success": True, "commands_visible": False},
        }
        assert response.json() == control_results[method]


def test_get_requests_do_not_mutate_facade(client, facade):
    before_state = deepcopy(facade.state)
    before_calls = len(facade.calls)
    for path in ("/api/status", "/api/session", "/api/adaptation", "/api/commands"):
        assert client.get(path).status_code == 200
    assert facade.state == before_state
    assert len(facade.calls) == before_calls + 4


@pytest.mark.parametrize(
    ("path", "method"),
    [
        ("/api/status", "get_system_status"),
        ("/api/session", "get_session_metrics"),
        ("/api/adaptation", "get_adaptation_state"),
        ("/api/commands", "get_commands"),
        ("/api/system/suspend", "suspend"),
        ("/api/system/activate", "activate"),
        ("/api/commands/show", "show_commands"),
        ("/api/commands/hide", "hide_commands"),
    ],
)
def test_facade_failures_return_controlled_error_without_internal_details(path, method):
    client = TestClient(create_app(FakeFacade(fail=method)))
    response = client.get(path) if method.startswith("get_") else client.post(path)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal ZeroUI operation failed"}
    body = response.text.lower()
    assert "traceback" not in body
    assert "private" not in body
    assert "engine.py" not in body


def test_cors_allows_configured_local_frontend_origin(client):
    response = client.options(
        "/api/status",
        headers={
            "Origin": "http://localhost:8100",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:8100"


def test_cors_does_not_allow_arbitrary_external_origin(client):
    response = client.options(
        "/api/status",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers


def test_create_app_instances_keep_facade_state_isolated():
    first_facade = FakeFacade()
    second_facade = FakeFacade()
    first_client = TestClient(create_app(first_facade))
    second_client = TestClient(create_app(second_facade))

    assert first_client.post("/api/system/suspend").json()["suspended"] is True
    assert first_facade.state["active"] is False
    assert second_facade.state["active"] is True
    assert second_client.get("/api/status").json() == second_facade.status
    assert first_facade.calls == ["suspend"]
    assert second_facade.calls == ["get_system_status"]


def test_swagger_docs_remain_available(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()
