from domain.commands.system_actions import (
    SystemAction
)

import threading

from domain.events.event_types import (
    EventType
)


class MultimodalCoordinator:
    """
    Coordina la salida del motor multimodal.

    Recibe eventos desde EventBus,
    los procesa mediante FusionEngine
    y ejecuta solamente los eventos
    seleccionados.
    """

    def __init__(
        self,
        event_bus,
        fusion_engine,
        action_executor,
        mouse_controller,
        overlay_service=None, 
        zoom_service=None,
        fusion_window=0.08
    ):
        self.event_bus = event_bus
        self.fusion_engine = (
            fusion_engine
        )

        self.action_executor = (
            action_executor
        )

        self.mouse = (
            mouse_controller
        )

        self.overlay_service = (
            overlay_service
        )

        self.zoom_service = (
            zoom_service
        )

        self.fusion_window = (
            fusion_window
        )

        self._pending_events = []

        self._lock = threading.RLock()

        self._timer = None

        self.event_bus.subscribe_all(
            self._receive_event
        )

    def _receive_event(
        self,
        event
    ):
        """
        Recibe eventos procedentes
        de cualquier canal.
        """

        with self._lock:

            self._pending_events.append(
                event
            )

            if self._timer is None:

                self._timer = (
                    threading.Timer(
                        self.fusion_window,
                        self._flush
                    )
                )

                self._timer.daemon = True

                self._timer.start()

    def _flush(self):
        """
        Procesa conjuntamente los eventos
        recibidos dentro de una pequeña
        ventana temporal.
        """

        with self._lock:

            events = list(
                self._pending_events
            )

            self._pending_events.clear()

            self._timer = None

        if not events:
            return

        resolved_events = (
            self.fusion_engine
            .process_events(events)
        )

        for event in resolved_events:

            try:

                self._execute_event(
                    event
                )

            except Exception as error:

                print(
                    "ERROR MULTIMODAL: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

    def _execute_event(
        self,
        event
    ):
        """
        Ejecuta el evento aprobado
        por FusionEngine.
        """

        if (
            event.event_type
            == EventType.ACTION
        ):

            if event.action is None:
                return

            if (
                event.action
                == SystemAction.DRAW
                and self.overlay_service
                is not None
            ):

                self.overlay_service \
                    .toggle_draw()

                return

            if (
                event.action
                == SystemAction.ERASE
                and self.overlay_service
                is not None
            ):

                self.overlay_service \
                    .toggle_erase()

                return

            if (
                event.action
                == SystemAction.ZOOM_IN
                and self.zoom_service
                is not None
            ):
            
                self.zoom_service.zoom_in()
            
                return
            
            
            if (
                event.action
                == SystemAction.ZOOM_OUT
                and self.zoom_service
                is not None
            ):
            
                self.zoom_service.zoom_out()
            
                return

            self.action_executor.execute(
                event.action
            )

            return

        if (
            event.event_type
            == EventType.CURSOR_MOVE
        ):

            mode = event.payload.get(
                "mode"
            )

            if mode == "relative":

                dx = event.payload.get(
                    "dx",
                    0
                )

                dy = event.payload.get(
                    "dy",
                    0
                )

                self.mouse.move_relative(
                    dx,
                    dy
                )

                return

            if mode == "absolute":

                x = event.payload.get(
                    "x"
                )

                y = event.payload.get(
                    "y"
                )

                if (
                    x is not None
                    and y is not None
                ):

                    self.mouse.move_to(
                        x,
                        y
                    )

    def stop(self):
        """
        Cancela el temporizador pendiente.
        """

        with self._lock:

            if self._timer is not None:

                self._timer.cancel()

                self._timer = None

            self._pending_events.clear()