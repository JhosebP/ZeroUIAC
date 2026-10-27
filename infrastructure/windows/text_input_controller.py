import math
import threading
import time

import pyautogui
import pyperclip


class TextInputController:
    """
    Permite escribir texto reconocido
    por voz en la aplicación activa
    de Windows.

    Se utiliza el portapapeles para
    conservar correctamente caracteres
    Unicode como:

    á é í ó ú ñ ¿ ¡
    """

    # Serialize clipboard transactions across controller instances.
    _clipboard_lock = threading.Lock()

    def __init__(
        self,
        paste_delay=0.30
    ):

        pyautogui.PAUSE = 0

        delay = float(paste_delay)
        if not math.isfinite(delay) or delay < 0:
            raise ValueError("paste_delay must be finite and non-negative")
        self.paste_delay = delay

    def write_text(
        self,
        text,
        add_space=True
    ):
        """
        Inserta texto en la aplicación
        que actualmente tiene el foco.

        Restaura el texto previo del portapapeles si no detecta
        una copia externa posterior. True confirma el envío de Ctrl+V
        sin fallos detectados; no confirma que el destino lo consumió.
        False también puede indicar un fallo de restauración después
        de haber enviado el pegado: no se debe reintentar automáticamente.
        """

        if text is None:
            return False

        text = str(text).strip()

        if not text:
            return False

        if add_space:
            text += " "

        with self._clipboard_lock:
            try:
                previous_clipboard = pyperclip.paste()
            except Exception:
                # Do not replace content that we cannot back up.
                return False

            success = False
            paste_attempted = False
            try:
                pyperclip.copy(text)
                if pyperclip.paste() == text:
                    # A failed hotkey may already have sent some keys.
                    paste_attempted = True
                    pyautogui.hotkey("ctrl", "v")
                    success = True
            except Exception:
                success = False
            finally:
                try:
                    # Ctrl+V dispatch does not acknowledge consumption by
                    # Word. Keep the text available for a configurable GUI
                    # grace period (300 ms by default), even if hotkey fails.
                    if paste_attempted and self.paste_delay > 0:
                        time.sleep(self.paste_delay)
                except Exception:
                    success = False
                finally:
                    try:
                        # Preserve a newer clipboard value from another app.
                        if pyperclip.paste() == text:
                            pyperclip.copy(previous_clipboard)
                            if pyperclip.paste() != previous_clipboard:
                                success = False
                    except Exception:
                        success = False

            # True confirms dispatch and no detected transaction failure;
            # the destination application's actual insertion needs validation.
            return success
