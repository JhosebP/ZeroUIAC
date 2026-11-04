"""Thread-managed Uvicorn server for the local ZeroUI API."""

import threading

import uvicorn


class LocalApiServer:
    """Run one Uvicorn server without blocking the application's main thread."""

    def __init__(
        self,
        app,
        *,
        host="127.0.0.1",
        port=8765,
        on_error=None,
    ):
        self.host = host
        self.port = port
        self._app = app
        self._on_error = on_error
        self._lock = threading.RLock()
        self._server = None
        self._thread = None
        self._start_requested = False
        self._stop_requested = False
        self._error_reported = False

    def start(self):
        """Start the server thread once; return without waiting for bind/startup."""
        with self._lock:
            if self._start_requested or self._stop_requested:
                return False

            config = uvicorn.Config(
                self._app,
                host=self.host,
                port=self.port,
                log_level="critical",
                access_log=False,
                timeout_graceful_shutdown=5.0,
            )
            self._server = uvicorn.Server(config)
            self._start_requested = True
            self._thread = threading.Thread(
                target=self._run,
                name="ZeroUI-LocalApi",
                daemon=True,
            )
            try:
                self._thread.start()
            except Exception:
                self._thread = None
                self._server = None
                self._start_requested = False
                raise
            return True

    def _run(self):
        failed = False
        try:
            self._server.run()
        except Exception:
            failed = True
        finally:
            with self._lock:
                failed = failed or not self._stop_requested
            if failed:
                self._report_error()

    def _report_error(self):
        with self._lock:
            if self._error_reported:
                return
            self._error_reported = True
            callback = self._on_error
        if callback is not None:
            try:
                callback()
            except Exception:
                # An API status callback must not affect the host application.
                pass

    def stop(self):
        """Request shutdown and join the worker; safe before or after start."""
        with self._lock:
            self._stop_requested = True
            server = self._server
            thread = self._thread
            if server is not None:
                server.should_exit = True

        if thread is not None and thread is not threading.current_thread():
            thread.join()

        with self._lock:
            if thread is self._thread and (thread is None or not thread.is_alive()):
                self._thread = None
                self._server = None
                self._app = None
