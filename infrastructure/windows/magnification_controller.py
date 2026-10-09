import ctypes
import queue
import threading

from ctypes import wintypes


class MagnificationController:
    """
    Controla la API nativa de ampliación
    de Windows.

    Todas las llamadas a la API de
    Magnification se ejecutan desde
    un único hilo permanente.
    """

    MIN_ZOOM = 1.0
    MAX_ZOOM = 4.0

    def __init__(self):

        self._dll = ctypes.WinDLL(
            "Magnification.dll"
        )

        self._configure_api()

        self._commands = (
            queue.Queue()
        )

        self._ready = (
            threading.Event()
        )

        self._initialized = False

        self._closed = False

        self._worker_thread = (
            threading.Thread(
                target=self._worker,
                name=(
                    "ZeroUI-Magnification"
                ),
                daemon=False
            )
        )

        self._worker_thread.start()

        self._ready.wait(
            timeout=3.0
        )

    def _configure_api(self):

        self._dll.MagInitialize.argtypes = []

        self._dll.MagInitialize.restype = (
            wintypes.BOOL
        )

        self._dll.MagUninitialize.argtypes = []

        self._dll.MagUninitialize.restype = (
            wintypes.BOOL
        )

        self._dll.MagSetFullscreenTransform.argtypes = [
            ctypes.c_float,
            ctypes.c_int,
            ctypes.c_int
        ]

        self._dll.MagSetFullscreenTransform.restype = (
            wintypes.BOOL
        )

    def _worker(self):

        try:

            self._initialized = bool(
                self._dll
                .MagInitialize()
            )

        finally:

            self._ready.set()

        if not self._initialized:
            return

        try:

            while True:

                command = (
                    self._commands.get()
                )

                command_type = (
                    command["type"]
                )

                if command_type == "close":

                    command["result"][0] = (
                        True
                    )

                    command["event"].set()

                    break

                try:

                    if command_type == "zoom":

                        result = (
                            self._apply_zoom(
                                level=(
                                    command["level"]
                                ),
                                focus_x=(
                                    command["focus_x"]
                                ),
                                focus_y=(
                                    command["focus_y"]
                                ),
                                screen_width=(
                                    command[
                                        "screen_width"
                                    ]
                                ),
                                screen_height=(
                                    command[
                                        "screen_height"
                                    ]
                                )
                            )
                        )

                    elif (
                        command_type
                        == "reset"
                    ):

                        result = (
                            self._reset_native()
                        )

                    else:

                        result = False

                    command["result"][0] = (
                        result
                    )

                except Exception as error:

                    print(
                        "ERROR MAGNIFICATION: "
                        f"{type(error).__name__}: "
                        f"{error}"
                    )

                    command["result"][0] = (
                        False
                    )

                finally:

                    command["event"].set()

        finally:

            try:

                self._reset_native()

            except Exception:
                pass

            try:

                self._dll \
                    .MagUninitialize()

            except Exception:
                pass

            self._initialized = False

    def initialize(self):

        self._ready.wait(
            timeout=3.0
        )

        return (
            self._initialized
        )

    def _send_command(
        self,
        command
    ):

        if self._closed:
            return False

        if not self.initialize():
            return False

        finished = (
            threading.Event()
        )

        result = [False]

        command["event"] = (
            finished
        )

        command["result"] = (
            result
        )

        self._commands.put(
            command
        )

        completed = finished.wait(
            timeout=3.0
        )

        if not completed:

            print(
                "ERROR MAGNIFICATION: "
                "tiempo de espera agotado."
            )

            return False

        return bool(
            result[0]
        )

    def set_zoom(
        self,
        level,
        focus_x,
        focus_y,
        screen_width,
        screen_height
    ):

        level = max(
            self.MIN_ZOOM,
            min(
                self.MAX_ZOOM,
                float(level)
            )
        )

        return self._send_command(
            {
                "type": "zoom",
                "level": level,
                "focus_x": focus_x,
                "focus_y": focus_y,
                "screen_width": (
                    screen_width
                ),
                "screen_height": (
                    screen_height
                )
            }
        )

    def _apply_zoom(
        self,
        level,
        focus_x,
        focus_y,
        screen_width,
        screen_height
    ):

        if level <= 1.0:

            return self._reset_native()

        visible_width = (
            screen_width
            / level
        )

        visible_height = (
            screen_height
            / level
        )

        x_offset = (
            focus_x
            - visible_width / 2
        )

        y_offset = (
            focus_y
            - visible_height / 2
        )

        max_x_offset = max(
            0,
            screen_width
            - visible_width
        )

        max_y_offset = max(
            0,
            screen_height
            - visible_height
        )

        x_offset = max(
            0,
            min(
                max_x_offset,
                x_offset
            )
        )

        y_offset = max(
            0,
            min(
                max_y_offset,
                y_offset
            )
        )

        result = (
            self._dll
            .MagSetFullscreenTransform(
                ctypes.c_float(
                    level
                ),
                int(
                    x_offset
                ),
                int(
                    y_offset
                )
            )
        )

        return bool(
            result
        )

    def reset(self):

        return self._send_command(
            {
                "type": "reset"
            }
        )

    def _reset_native(self):

        result = (
            self._dll
            .MagSetFullscreenTransform(
                ctypes.c_float(1.0),
                0,
                0
            )
        )

        return bool(
            result
        )

    def close(self):

        if self._closed:
            return

        if not self._worker_thread \
                .is_alive():

            self._closed = True

            return

        finished = (
            threading.Event()
        )

        result = [False]

        self._commands.put(
            {
                "type": "close",
                "event": finished,
                "result": result
            }
        )

        finished.wait(
            timeout=3.0
        )

        self._worker_thread.join(
            timeout=3.0
        )

        self._closed = True