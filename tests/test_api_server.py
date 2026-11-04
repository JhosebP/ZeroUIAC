import threading

import pytest

from presentation.api.server import LocalApiServer


@pytest.fixture
def fake_uvicorn(monkeypatch):
    state = {"configs": [], "servers": []}

    class FakeConfig:
        def __init__(self, app, **kwargs):
            self.app = app
            self.kwargs = kwargs
            state["configs"].append(self)

    class FakeServer:
        def __init__(self, config):
            self.config = config
            self.started = False
            self.entered = threading.Event()
            self._should_exit = False
            self._exit_requested = threading.Event()
            self.fail = state.pop("fail_next", False)
            state["servers"].append(self)

        @property
        def should_exit(self):
            return self._should_exit

        @should_exit.setter
        def should_exit(self, value):
            self._should_exit = value
            if value:
                self._exit_requested.set()

        def run(self):
            if self.fail:
                raise OSError("simulated bind failure")
            self.started = True
            self.entered.set()
            self._exit_requested.wait()
            self.started = False

    monkeypatch.setattr("presentation.api.server.uvicorn.Config", FakeConfig)
    monkeypatch.setattr("presentation.api.server.uvicorn.Server", FakeServer)
    return state


def test_server_uses_loopback_and_expected_port(fake_uvicorn):
    server = LocalApiServer(object())
    assert server.start() is True
    config = fake_uvicorn["configs"][0]
    assert config.kwargs["host"] == "127.0.0.1"
    assert config.kwargs["port"] == 8765
    server.stop()


def test_start_returns_while_server_runs_in_background(fake_uvicorn):
    server = LocalApiServer(object())
    assert server.start() is True
    running = fake_uvicorn["servers"][0]
    assert running.entered.wait(timeout=1)
    assert server._thread.is_alive()
    server.stop()


def test_start_twice_creates_only_one_server_and_thread(fake_uvicorn):
    server = LocalApiServer(object())
    assert server.start() is True
    running = fake_uvicorn["servers"][0]
    assert running.entered.wait(timeout=1)
    thread = server._thread
    assert server.start() is False
    assert len(fake_uvicorn["configs"]) == 1
    assert len(fake_uvicorn["servers"]) == 1
    assert server._thread is thread
    server.stop()


def test_stop_requests_server_shutdown(fake_uvicorn):
    server = LocalApiServer(object())
    server.start()
    running = fake_uvicorn["servers"][0]
    assert running.entered.wait(timeout=1)
    server.stop()
    assert running.should_exit is True
    assert running.started is False


def test_stop_twice_is_safe(fake_uvicorn):
    server = LocalApiServer(object())
    server.start()
    assert fake_uvicorn["servers"][0].entered.wait(timeout=1)
    server.stop()
    server.stop()
    assert server._thread is None
    assert server._server is None


def test_stop_without_start_is_safe():
    server = LocalApiServer(object())
    server.stop()
    server.stop()
    assert server._thread is None
    assert server._server is None
    assert server.start() is False


def test_startup_failure_is_reported_without_escaping_host_thread(fake_uvicorn):
    failures = []
    reported = threading.Event()

    def on_error():
        failures.append(threading.get_ident())
        reported.set()

    state = fake_uvicorn
    state["fail_next"] = True
    host_thread = threading.get_ident()
    server = LocalApiServer(object(), on_error=on_error)
    server.start()
    worker = server._thread
    assert reported.wait(timeout=1)
    assert failures == [worker.ident]
    assert failures[0] != host_thread
    assert worker is not threading.current_thread()
    server.stop()


def test_worker_thread_terminates_and_references_are_cleared(fake_uvicorn):
    server = LocalApiServer(object())
    server.start()
    assert fake_uvicorn["servers"][0].entered.wait(timeout=1)
    worker = server._thread
    server.stop()
    assert not worker.is_alive()
    assert server._thread is None
    assert server._server is None
    assert server._app is None
