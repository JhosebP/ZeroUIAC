class ZoomService:
    """
    Gestiona el nivel de zoom
    de ZeroUI-AC.

    Rango:
    100 % a 400 %

    Incremento:
    25 %
    """

    MIN_ZOOM = 1.0
    MAX_ZOOM = 4.0
    ZOOM_STEP = 0.25

    def __init__(
        self,
        magnification_controller,
        mouse_controller
    ):
        self.magnification = (
            magnification_controller
        )

        self.mouse = (
            mouse_controller
        )

        self.current_zoom = (
            self.MIN_ZOOM
        )

    def _apply_zoom(self):

        cursor_x, cursor_y = (
            self.mouse
            .get_position()
        )

        screen_width, screen_height = (
            self.mouse
            .get_screen_size()
        )

        return (
            self.magnification
            .set_zoom(
                level=self.current_zoom,
                focus_x=cursor_x,
                focus_y=cursor_y,
                screen_width=(
                    screen_width
                ),
                screen_height=(
                    screen_height
                )
            )
        )

    def zoom_in(self):

        new_zoom = min(
            self.MAX_ZOOM,
            self.current_zoom
            + self.ZOOM_STEP
        )

        if (
            new_zoom
            == self.current_zoom
        ):
            return False

        self.current_zoom = (
            new_zoom
        )

        result = (
            self._apply_zoom()
        )

        if result:

            print(
                "Zoom: "
                f"{int(self.current_zoom * 100)}%"
            )

        return result

    def zoom_out(self):

        new_zoom = max(
            self.MIN_ZOOM,
            self.current_zoom
            - self.ZOOM_STEP
        )

        if (
            new_zoom
            == self.current_zoom
        ):
            return False

        self.current_zoom = (
            new_zoom
        )

        result = (
            self._apply_zoom()
        )

        if result:

            print(
                "Zoom: "
                f"{int(self.current_zoom * 100)}%"
            )

        return result

    def reset(self):

        self.current_zoom = (
            self.MIN_ZOOM
        )

        return (
            self.magnification
            .reset()
        )

    def close(self):

        self.current_zoom = (
            self.MIN_ZOOM
        )

        self.magnification.close()