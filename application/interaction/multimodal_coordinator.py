import threading

from domain.commands.system_actions import (
    SystemAction
)

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

    También genera retroalimentación
    visual y auditiva después de
    ejecutar acciones.
    """

    ACTION_LABELS = {
        SystemAction.LEFT_CLICK:
            "Clic",

        SystemAction.RIGHT_CLICK:
            "Clic derecho",

        SystemAction.DOUBLE_CLICK:
            "Doble clic",

        SystemAction.START_DRAG:
            "Arrastrar",

        SystemAction.STOP_DRAG:
            "Soltar",

        SystemAction.COPY:
            "Copiar",

        SystemAction.PASTE:
            "Pegar",

        SystemAction.CUT:
            "Cortar",

        SystemAction.UNDO:
            "Deshacer",

        SystemAction.SAVE:
            "Guardar",

        SystemAction.SELECT_ALL:
            "Seleccionar todo",

        SystemAction.DELETE:
            "Eliminar",

        SystemAction.SWITCH_APP:
            "Cambiar aplicación",

        SystemAction.NAV_UP:
            "Arriba",

        SystemAction.NAV_DOWN:
            "Abajo",

        SystemAction.NAV_LEFT:
            "Izquierda",

        SystemAction.NAV_RIGHT:
            "Derecha",
    }

    def __init__(
        self,
        event_bus,
        fusion_engine,
        action_executor,
        mouse_controller,
        overlay_service=None,
        zoom_service=None,
        audio_feedback_service=None,
        session_manager=None,
        fusion_window=0.08
    ):

        self.event_bus = (
            event_bus
        )

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

        self.audio_feedback_service = (
            audio_feedback_service
        )

        self.session_manager = (
            session_manager
        )

        self.fusion_window = (
            fusion_window
        )

        self._pending_events = []

        self._lock = (
            threading.RLock()
        )

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

    def _record_session_event(
        self,
        event
    ):
        """
        Registra únicamente eventos que
        ya fueron aceptados por FusionEngine.

        Un fallo en las métricas nunca debe
        interrumpir la interacción principal.
        """

        if self.session_manager is None:
            return

        try:

            self.session_manager.record_event(
                event
            )

        except Exception as error:

            print(
                "ERROR METRICAS DE SESION: "
                f"{type(error).__name__}: "
                f"{error}"
            )

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
            .process_events(
                events
            )
        )

        for event in resolved_events:

            self._record_session_event(
                event
            )

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

                self._show_error_feedback(
                    "No se pudo ejecutar la acción"
                )

    def _show_feedback(
        self,
        text
    ):
        """
        Solicita mostrar una confirmación
        visual mediante el overlay.
        """

        if (
            self.overlay_service
            is None
        ):

            return

        self.overlay_service \
            .show_feedback(
                text
            )

    def _show_error_feedback(
        self,
        text
    ):
        """
        Muestra un mensaje de error
        diferenciado en el overlay.
        """
    
        if (
            self.overlay_service
            is None
        ):
    
            return
    
        self.overlay_service \
            .show_error_feedback(
                text
            )

    def _play_audio_feedback(self):
        """
        Reproduce el tono de confirmación
        cuando el servicio de audio
        se encuentra disponible.
        """

        if (
            self.audio_feedback_service
            is None
        ):

            return

        self.audio_feedback_service \
            .play_success()

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

            # -----------------------------
            # DIBUJO
            # -----------------------------

            if (
                event.action
                == SystemAction.DRAW
                and self.overlay_service
                is not None
            ):

                self.overlay_service \
                    .toggle_draw()

                if (
                    self.overlay_service
                    .is_active
                    and self.overlay_service
                    .mode
                    == self.overlay_service
                    .MODE_DRAW
                ):

                    self._show_feedback(
                        "Dibujo activado"
                    )

                else:

                    self._show_feedback(
                        "Dibujo desactivado"
                    )

                self._play_audio_feedback()

                return

            # -----------------------------
            # ACTIVAR BORRADOR
            # -----------------------------
            
            if (
                event.action
                == SystemAction.ERASER_ON
            ):
            
                if self.overlay_service is None:
                
                    self._show_error_feedback(
                        "Borrador no disponible"
                    )
            
                    return
            
                if not (
                    self.overlay_service.is_active
                    and self.overlay_service.mode
                    == self.overlay_service.MODE_ERASE
                ):
            
                    self.overlay_service \
                        .toggle_erase()
            
                self._show_feedback(
                    "Borrador activado"
                )
            
                self._play_audio_feedback()
            
                return
            
            
            # -----------------------------
            # DESACTIVAR BORRADOR
            # -----------------------------
            
            if (
                event.action
                == SystemAction.ERASER_OFF
            ):
            
                if self.overlay_service is None:
                
                    return
            
                if (
                    self.overlay_service.is_active
                    and self.overlay_service.mode
                    == self.overlay_service.MODE_ERASE
                ):
            
                    self.overlay_service \
                        .toggle_erase()
            
                self._show_feedback(
                    "Borrador desactivado"
                )
            
                self._play_audio_feedback()
            
                return

            # -----------------------------
            # BORRADOR
            # -----------------------------

            if (
                event.action
                == SystemAction.ERASE
                and self.overlay_service
                is not None
            ):

                self.overlay_service \
                    .toggle_erase()

                if (
                    self.overlay_service
                    .is_active
                    and self.overlay_service
                    .mode
                    == self.overlay_service
                    .MODE_ERASE
                ):

                    self._show_feedback(
                        "Borrador activado"
                    )

                else:

                    self._show_feedback(
                        "Borrador desactivado"
                    )

                self._play_audio_feedback()

                return

            # -----------------------------
            # ZOOM IN
            # -----------------------------

            if (
                event.action
                == SystemAction.ZOOM_IN
                and self.zoom_service
                is not None
            ):

                result = (
                    self.zoom_service
                    .zoom_in()
                )

                if result:

                    percentage = int(
                        self.zoom_service
                        .current_zoom
                        * 100
                    )

                    self._show_feedback(
                        f"Zoom {percentage}%"
                    )

                    self._play_audio_feedback()

                return

            # -----------------------------
            # ZOOM OUT
            # -----------------------------

            if (
                event.action
                == SystemAction.ZOOM_OUT
                and self.zoom_service
                is not None
            ):

                result = (
                    self.zoom_service
                    .zoom_out()
                )

                if result:

                    percentage = int(
                        self.zoom_service
                        .current_zoom
                        * 100
                    )

                    self._show_feedback(
                        f"Zoom {percentage}%"
                    )

                    self._play_audio_feedback()

                return

            # -----------------------------
            # ACCIONES NORMALES
            # -----------------------------

            self.action_executor.execute(
                event.action
            )

            label = (
                self.ACTION_LABELS
                .get(
                    event.action
                )
            )

            if label is not None:

                self._show_feedback(
                    label
                )

            self._play_audio_feedback()

            return

        if (
            event.event_type
            == EventType.STATUS
        ):
        
            payload = (
                event.payload
                or {}
            )
        
            level = (
                payload.get(
                    "level"
                )
            )
        
            message = (
                payload.get(
                    "message"
                )
            )
        
            if (
                level == "error"
                and message
            ):
        
                self._show_error_feedback(
                    message
                )
        
                return
        
            if (
                level == "success"
                and message
            ):
        
                self._show_feedback(
                    message
                )
        
                if (
                    self.audio_feedback_service
                    is not None
                ):
        
                    self.audio_feedback_service \
                        .play_success()
        
                return
        
            return

        # -----------------------------
        # MOVIMIENTO DEL CURSOR
        # -----------------------------

        if (
            event.event_type
            == EventType.CURSOR_MOVE
        ):

            mode = (
                event.payload.get(
                    "mode"
                )
            )

            if mode == "relative":

                dx = (
                    event.payload.get(
                        "dx",
                        0
                    )
                )

                dy = (
                    event.payload.get(
                        "dy",
                        0
                    )
                )

                self.mouse.move_relative(
                    dx,
                    dy
                )

                return

            if mode == "absolute":

                x = (
                    event.payload.get(
                        "x"
                    )
                )

                y = (
                    event.payload.get(
                        "y"
                    )
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