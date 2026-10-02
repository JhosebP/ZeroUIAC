import ctypes
import threading
import tkinter as tk

import pyautogui
import math

class AnnotationOverlay:
    """
    Capa transparente de anotación
    para ZeroUI-AC.

    Permite dibujar y borrar siguiendo
    la posición actual del cursor.

    Está diseñada para Windows.
    """

    MODE_DRAW = "draw"
    MODE_ERASE = "erase"

    def __init__(
        self,
        line_width=5,
        eraser_radius=25,
        refresh_ms=16,
        max_draw_jump=80
    ):
        self.line_width = line_width

        self.eraser_radius = (
            eraser_radius
        )

        self.refresh_ms = (
            refresh_ms
        )

        self.max_draw_jump = (
            max_draw_jump
        )

        self._active = False

        self._mode = None

        self._lock = (
            threading.RLock()
        )

        self._thread = None

        self._stop_event = (
            threading.Event()
        )

        self._root = None
        self._canvas = None

        self._last_point = None

        self._clear_version = 0
        self._processed_clear_version = 0

    @property
    def is_active(self):

        with self._lock:

            return self._active

    @property
    def mode(self):

        with self._lock:

            return self._mode

    def toggle_draw(self):
        """
        Activa/desactiva el modo dibujo.
        """

        with self._lock:

            if (
                self._active
                and self._mode
                == self.MODE_DRAW
            ):

                self._active = False
                self._mode = None

            else:

                self._active = True

                self._mode = (
                    self.MODE_DRAW
                )

            self._last_point = None

    def toggle_erase(self):
        """
        Activa/desactiva el borrador.
        """

        with self._lock:

            if (
                self._active
                and self._mode
                == self.MODE_ERASE
            ):

                self._active = False
                self._mode = None

            else:

                self._active = True

                self._mode = (
                    self.MODE_ERASE
                )

            self._last_point = None

    def deactivate(self):
        """
        Oculta el overlay.
        """

        with self._lock:

            self._active = False
            self._mode = None

            self._last_point = None

    def clear(self):
        """
        Solicita borrar todas
        las anotaciones.
        """

        with self._lock:

            self._clear_version += 1

    def start(self):
        """
        Inicia el overlay en su
        propio hilo de interfaz.
        """

        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return

        self._stop_event.clear()

        self._thread = (
            threading.Thread(
                target=self._run,
                daemon=False
            )
        )

        self._thread.start()

    def stop(self):
        """
        Solicita el cierre del overlay
        y espera que Tkinter finalice
        desde su propio hilo.
        """

        self._stop_event.set()

        thread = self._thread

        if (
            thread is not None
            and thread.is_alive()
        ):

            thread.join(
                timeout=3
            )

        if (
            thread is not None
            and thread.is_alive()
        ):

            print(
                "ADVERTENCIA: el overlay "
                "no finalizó completamente."
            )

        else:

            self._thread = None

    def _make_click_through(self):
        """
        Permite que la ventana no
        bloquee las aplicaciones
        ubicadas debajo.
        """

        try:

            hwnd = (
                self._root
                .winfo_id()
            )

            parent = (
                ctypes.windll
                .user32
                .GetParent(hwnd)
            )

            if parent:
                hwnd = parent

            GWL_EXSTYLE = -20

            WS_EX_LAYERED = (
                0x00080000
            )

            WS_EX_TRANSPARENT = (
                0x00000020
            )

            WS_EX_TOOLWINDOW = (
                0x00000080
            )

            WS_EX_NOACTIVATE = (
                0x08000000
            )

            style = (
                ctypes.windll
                .user32
                .GetWindowLongW(
                    hwnd,
                    GWL_EXSTYLE
                )
            )

            style |= (
                WS_EX_LAYERED
                | WS_EX_TRANSPARENT
                | WS_EX_TOOLWINDOW
                | WS_EX_NOACTIVATE
            )

            ctypes.windll \
                .user32 \
                .SetWindowLongW(
                    hwnd,
                    GWL_EXSTYLE,
                    style
                )

        except Exception as error:

            print(
                "Aviso overlay "
                "click-through:",
                error
            )

    def _run(self):
        """
        Ejecuta la ventana transparente.
        """

        try:

            try:

                ctypes.windll \
                    .user32 \
                    .SetProcessDPIAware()

            except Exception:
                pass

            self._root = tk.Tk()

            self._root.title(
                "ZeroUI-AC Overlay"
            )

            self._root.overrideredirect(
                True
            )

            self._root.attributes(
                "-topmost",
                True
            )

            screen_width = (
                self._root
                .winfo_screenwidth()
            )

            screen_height = (
                self._root
                .winfo_screenheight()
            )

            self._root.geometry(
                (
                    f"{screen_width}x"
                    f"{screen_height}"
                    "+0+0"
                )
            )

            self._root.configure(
                bg="black"
            )

            try:

                self._root.attributes(
                    "-transparentcolor",
                    "black"
                )

            except tk.TclError:
                pass

            self._canvas = tk.Canvas(
                self._root,
                width=screen_width,
                height=screen_height,
                bg="black",
                highlightthickness=0,
                borderwidth=0
            )

            self._canvas.pack(
                fill="both",
                expand=True
            )

            self._root.withdraw()

            self._root.update_idletasks()

            self._make_click_through()

            self._root.after(
                self.refresh_ms,
                self._tick
            )

            self._root.mainloop()

        except Exception as error:

            print(
                "ERROR EN OVERLAY:",
                error
            )

        finally:

            self._canvas = None
            self._root = None

    def _tick(self):
        """
        Actualiza dibujo/borrado.
        """

        if self._stop_event.is_set():

            if self._root is not None:

                try:

                    self._root.quit()
                    self._root.destroy()

                except tk.TclError:
                    pass

            return

        with self._lock:

            active = self._active
            mode = self._mode

            clear_version = (
                self._clear_version
            )

        if (
            clear_version
            != self._processed_clear_version
        ):

            if self._canvas is not None:

                self._canvas.delete(
                    "all"
                )

            self._processed_clear_version = (
                clear_version
            )

        if not active:

            if (
                self._root is not None
                and self._root
                .state()
                != "withdrawn"
            ):

                self._root.withdraw()

            self._last_point = None

        else:

            if (
                self._root is not None
                and self._root
                .state()
                == "withdrawn"
            ):

                self._root.deiconify()

                self._root.lift()

            position = (
                pyautogui.position()
            )

            x = position.x
            y = position.y

            if mode == self.MODE_DRAW:

                self._draw(
                    x,
                    y
                )

            elif mode == self.MODE_ERASE:

                self._erase(
                    x,
                    y
                )

        if self._root is not None:

            self._root.after(
                self.refresh_ms,
                self._tick
            )

    def _draw(
        self,
        x,
        y
    ):
        """
        Dibuja siguiendo el cursor.

        Si existe un salto demasiado grande,
        interrumpe el trazo para evitar
        líneas producidas por pérdida de
        seguimiento.
        """

        if self._last_point is None:

            self._last_point = (
                x,
                y
            )

            return

        previous_x, previous_y = (
            self._last_point
        )

        delta_x = (
            x - previous_x
        )

        delta_y = (
            y - previous_y
        )

        distance = math.sqrt(
            delta_x ** 2
            + delta_y ** 2
        )

        if (
            distance
            > self.max_draw_jump
        ):

            self._last_point = (
                x,
                y
            )

            return

        if (
            previous_x == x
            and previous_y == y
        ):
            return

        self._canvas.create_line(
            previous_x,
            previous_y,
            x,
            y,
            fill="red",
            width=self.line_width,
            capstyle=tk.ROUND,
            smooth=True
        )

        self._last_point = (
            x,
            y
        )

    

        """
        Dibuja siguiendo el cursor.
        """

        if self._last_point is None:

            self._last_point = (
                x,
                y
            )

            return

        previous_x, previous_y = (
            self._last_point
        )

        if (
            previous_x == x
            and previous_y == y
        ):
            return

        self._canvas.create_line(
            previous_x,
            previous_y,
            x,
            y,
            fill="red",
            width=self.line_width,
            capstyle=tk.ROUND,
            smooth=True
        )

        self._last_point = (
            x,
            y
        )

    def _erase(
        self,
        x,
        y
    ):
        """
        Elimina trazos cercanos
        a la posición del cursor.
        """

        radius = (
            self.eraser_radius
        )

        items = (
            self._canvas
            .find_overlapping(
                x - radius,
                y - radius,
                x + radius,
                y + radius
            )
        )

        for item in items:

            self._canvas.delete(
                item
            )

        self._last_point = None

    def break_stroke(self):
        """
        Interrumpe el trazo actual sin
        desactivar el modo dibujo.
        """
    
        with self._lock:
        
            self._last_point = None