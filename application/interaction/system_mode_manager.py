import threading
import time
from contextlib import contextmanager


class SystemModeManager:
    """Shared admission barrier for input processing and suspend/resume."""

    def __init__(self, clock=None):
        self._lock = threading.RLock()
        self._clock = clock or time.monotonic
        self._suspended = False
        self._generation = 0
        self._accept_after = float('-inf')

    def suspend(self):
        # In-flight admitted work finishes before this transition returns.
        with self._lock:
            if not self._suspended:
                self._suspended = True
                self._generation += 1
                self._accept_after = self._clock()

    def activate(self):
        with self._lock:
            if self._suspended:
                self._suspended = False
                self._generation += 1
                self._accept_after = self._clock()

    def is_suspended(self):
        with self._lock:
            return self._suspended

    def is_active(self):
        return not self.is_suspended()

    @property
    def generation(self):
        with self._lock:
            return self._generation

    @contextmanager
    def processing(self, timestamp=None, generation=None):
        # Callers hold this barrier through execution and metric recording.
        # A timestamp rejects events queued before the latest transition.
        with self._lock:
            yield (
                not self._suspended
                and (timestamp is None or timestamp >= self._accept_after)
                and (generation is None or generation == self._generation)
            )
