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

    def __init__(
        self,
        paste_delay=0.05
    ):

        pyautogui.PAUSE = 0

        self.paste_delay = paste_delay

    def write_text(
        self,
        text,
        add_space=True
    ):
        """
        Inserta texto en la aplicación
        que actualmente tiene el foco.

        El contenido previo del portapapeles
        se restaura después de escribir.
        """

        if text is None:
            return False

        text = str(text).strip()

        if not text:
            return False

        if add_space:
            text += " "

        previous_clipboard = None

        try:

            previous_clipboard = (
                pyperclip.paste()
            )

        except Exception:
            pass

        try:

            pyperclip.copy(text)

            pyautogui.hotkey(
                "ctrl",
                "v"
            )

            if self.paste_delay > 0:
                time.sleep(
                    self.paste_delay
                )

        finally:

            if (
                previous_clipboard
                is not None
            ):

                try:

                    pyperclip.copy(
                        previous_clipboard
                    )

                except Exception:
                    pass

        return True