import ctypes
import math
import threading
import time
import tkinter as tk

import pyautogui


class AnnotationOverlay:
    """
    Capa transparente de anotación
    para ZeroUI-AC.

    Permite:

    - dibujar;
    - borrar;
    - mostrar retroalimentación visual;
    - trabajar sin bloquear las aplicaciones
      que se encuentran debajo.

    Diseñada para Windows.
    """

    MODE_DRAW = "draw"
    MODE_ERASE = "erase"

    SM_CXSCREEN = 0

    SM_XVIRTUALSCREEN = 76
    SM_YVIRTUALSCREEN = 77
    SM_CXVIRTUALSCREEN = 78
    SM_CYVIRTUALSCREEN = 79

    def __init__(
        self,
        line_width=5,
        eraser_radius=25,
        refresh_ms=16,
        max_draw_jump=80,
        feedback_duration=1.5
    ):

        self.line_width = (
            line_width
        )

        self.eraser_radius = (
            eraser_radius
        )

        self.refresh_ms = (
            refresh_ms
        )

        self.max_draw_jump = (
            max_draw_jump
        )

        self.feedback_duration = (
            feedback_duration
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

        self._virtual_left = 0
        self._virtual_top = 0

        self._virtual_width = 0
        self._virtual_height = 0

        self._last_point = None

        self._clear_version = 0

        self._processed_clear_version = 0

        self._feedback_text = None

        self._feedback_type = "success"

        self._feedback_until = 0.0

        self._feedback_version = 0

        self._processed_feedback_version = 0

    @property
    def is_active(self):

        with self._lock:

            return self._active

    @property
    def mode(self):

        with self._lock:

            return self._mode

    @property
    def feedback_text(self):

        with self._lock:

            return self._feedback_text

    @property
    def feedback_type(self):
    
        with self._lock:
        
            return self._feedback_type

    def toggle_draw(self):
        """
        Activa o desactiva
        el modo dibujo.
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
        Activa o desactiva
        el modo borrador.
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
        Desactiva dibujo y borrado.
        """

        with self._lock:

            self._active = False

            self._mode = None

            self._last_point = None

    def clear(self):
        """
        Solicita eliminar todas
        las anotaciones dibujadas.
        """

        with self._lock:

            self._clear_version += 1

    def show_feedback(
        self,
        text,
        duration=None,
        feedback_type="success"
    ):
        """
        Solicita mostrar retroalimentación
        visual temporal.
        """

        if not text:
            return

        if duration is None:

            duration = (
                self.feedback_duration
            )

        feedback_type = (
            str(feedback_type)
            .lower()
        )

        if feedback_type not in (
            "success",
            "error"
        ):

            feedback_type = "success"

        with self._lock:

            self._feedback_text = (
                str(text)
            )

            self._feedback_type = (
                feedback_type
            )

            self._feedback_until = (
                time.monotonic()
                + float(duration)
            )

            self._feedback_version += 1


    def show_error_feedback(
        self,
        text,
        duration=None
    ):
        """
        Muestra retroalimentación
        visual de error.
        """

        self.show_feedback(
            text=text,
            duration=duration,
            feedback_type="error"
        )

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
                name="ZeroUI-Overlay",
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
                .GetParent(
                    hwnd
                )
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

    def _get_virtual_screen_bounds(
        self
    ):
        """
        Obtiene el rectángulo completo
        del escritorio virtual de Windows.
        """
    
        user32 = (
            ctypes.windll.user32
        )
    
        left = (
            user32.GetSystemMetrics(
                self.SM_XVIRTUALSCREEN
            )
        )
    
        top = (
            user32.GetSystemMetrics(
                self.SM_YVIRTUALSCREEN
            )
        )
    
        width = (
            user32.GetSystemMetrics(
                self.SM_CXVIRTUALSCREEN
            )
        )
    
        height = (
            user32.GetSystemMetrics(
                self.SM_CYVIRTUALSCREEN
            )
        )
    
        return (
            left,
            top,
            width,
            height
        )
    
    
    def _screen_to_canvas(
        self,
        x,
        y
    ):
        """
        Convierte coordenadas globales
        de Windows en coordenadas locales
        del Canvas del overlay.
        """
    
        canvas_x = (
            int(x)
            - self._virtual_left
        )
    
        canvas_y = (
            int(y)
            - self._virtual_top
        )
    
        return (
            canvas_x,
            canvas_y
        )
    
    
    def _build_virtual_geometry(
        self
    ):
        """
        Construye la geometría Tkinter
        para cubrir todo el escritorio
        virtual, incluso si existen
        coordenadas negativas.
        """
    
        return (
            f"{self._virtual_width}x"
            f"{self._virtual_height}"
            f"{self._virtual_left:+d}"
            f"{self._virtual_top:+d}"
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

            self._root = (
                tk.Tk()
            )

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

            (
                self._virtual_left,
                self._virtual_top,
                self._virtual_width,
                self._virtual_height
            ) = (
                self._get_virtual_screen_bounds()
            )
            
            screen_width = (
                self._virtual_width
            )
            
            screen_height = (
                self._virtual_height
            )
            
            self._root.geometry(
                self._build_virtual_geometry()
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

            self._canvas = (
                tk.Canvas(
                    self._root,
                    width=(
                        screen_width
                    ),
                    height=(
                        screen_height
                    ),
                    bg="black",
                    highlightthickness=0,
                    borderwidth=0
                )
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
        Actualiza:

        - dibujo;
        - borrado;
        - limpieza;
        - retroalimentación visual.
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

            active = (
                self._active
            )

            mode = (
                self._mode
            )

            clear_version = (
                self._clear_version
            )

            feedback_text = (
                self._feedback_text
            )

            feedback_type = (
                self._feedback_type
            )

            feedback_until = (
                self._feedback_until
            )

            feedback_version = (
                self._feedback_version
            )

        feedback_visible = (
            feedback_text is not None
            and time.monotonic()
            < feedback_until
        )

        if (
            clear_version
            != self._processed_clear_version
        ):

            if self._canvas is not None:

                self._canvas.delete(
                    "annotation"
                )

            self._processed_clear_version = (
                clear_version
            )

        if self._canvas is not None:

          self._set_annotations_visible(
              active
          )    

        if feedback_visible:

            if (
                feedback_version
                != self._processed_feedback_version
            ):

                self._render_feedback(
                    feedback_text,
                    feedback_type
                )

                self._processed_feedback_version = (
                    feedback_version
                )

        else:

            if self._canvas is not None:

                self._canvas.delete(
                    "feedback"
                )

        should_show_overlay = (
            active
            or feedback_visible
        )

        if not should_show_overlay:

            if (
                self._root is not None
                and self._root.state()
                != "withdrawn"
            ):

                self._root.withdraw()

            self._last_point = None

        else:

            if (
                self._root is not None
                and self._root.state()
                == "withdrawn"
            ):

                self._root.deiconify()

                self._root.lift()

            if active:

                position = (
                    pyautogui.position()
                )
                
                x, y = (
                    self._screen_to_canvas(
                        position.x,
                        position.y
                    )
                )

                if (
                    mode
                    == self.MODE_DRAW
                ):

                    self._draw(
                        x,
                        y
                    )

                elif (
                    mode
                    == self.MODE_ERASE
                ):

                    self._erase(
                        x,
                        y
                    )

            else:

                self._last_point = None

            if (
                feedback_visible
                and self._canvas
                is not None
            ):

                self._canvas.tag_raise(
                    "feedback"
                )

        if self._root is not None:

            self._root.after(
                self.refresh_ms,
                self._tick
            )

    def _set_annotations_visible(
        self,
        visible
    ):
        """
        Muestra u oculta las anotaciones
        sin eliminarlas del Canvas.
        """

        if self._canvas is None:
            return

        state = (
            "normal"
            if visible
            else "hidden"
        )

        self._canvas.itemconfigure(
            "annotation",
            state=state
        )

    def _render_feedback(
        self,
        text,
        feedback_type="success"
    ):
        """
        Dibuja la notificación visual
        en la esquina superior derecha.

        Los errores se muestran
        diferenciados en rojo.
        """

        if (
            self._canvas is None
            or self._root is None
        ):

            return

        self._canvas.delete(
            "feedback"
        )

        if feedback_type == "error":

            background = (
                "#B3261E"
            )

            icon = "✕"

        else:

            background = (
                "#245C45"
            )

            icon = "✓"

        primary_width = (
            ctypes.windll
            .user32
            .GetSystemMetrics(
                self.SM_CXSCREEN
            )
        )
        
        primary_left = (
            -self._virtual_left
        )
        
        primary_top = (
            -self._virtual_top
        )
        
        right = (
            primary_left
            + primary_width
            - 20
        )
        
        left = (
            right
            - 320
        )
        
        top = (
            primary_top
            + 25
        )
        
        bottom = (
            top
            + 60
        )

        self._canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill=background,
            outline="",
            tags=(
                "feedback",
            )
        )

        self._canvas.create_text(
            left + 20,
            (
                top
                + bottom
            ) / 2,
            text=(
                f"{icon} {text}"
            ),
            anchor="w",
            fill="white",
            font=(
                "Segoe UI",
                14,
                "bold"
            ),
            tags=(
                "feedback",
            )
        )

        self._canvas.tag_raise(
            "feedback"
        )

    def _draw(
        self,
        x,
        y
    ):
        """
        Dibuja siguiendo el cursor.

        Si existe un salto demasiado
        grande, interrumpe el trazo para
        evitar líneas producidas por
        pérdida temporal de seguimiento.
        """

        if self._canvas is None:

            return

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
            x
            - previous_x
        )

        delta_y = (
            y
            - previous_y
        )

        distance = (
            math.sqrt(
                delta_x ** 2
                + delta_y ** 2
            )
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
            width=(
                self.line_width
            ),
            capstyle=tk.ROUND,
            smooth=True,
            tags=(
                "annotation",
            )
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
        Elimina únicamente trazos
        de anotación cercanos al cursor.
        """

        if self._canvas is None:

            return

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

            tags = (
                self._canvas
                .gettags(
                    item
                )
            )

            if (
                "annotation"
                in tags
            ):

                self._canvas.delete(
                    item
                )

        self._last_point = None

    def break_stroke(self):
        """
        Interrumpe el trazo actual
        sin desactivar el modo dibujo.
        """

        with self._lock:

            self._last_point = None