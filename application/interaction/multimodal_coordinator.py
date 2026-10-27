import threading

from domain.commands.system_actions import (
    SystemAction
)

from domain.events.event_types import (
    EventType,
    EventSource,
)
from application.interaction.system_mode_manager import SystemModeManager
from modules.voice.voice_commands import SYSTEM_CONTROL_COMMANDS

#3ra capa de abstracción para los eventos de interacción del usuario.
#Agrupa y coordina eventos multimodales para su ejecución.

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

        SystemAction.ENTER:
            "Enter ejecutado",

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
        interaction_outcome_tracker=None,
        fusion_window=0.08,
        system_mode_manager=None,
    ):

        self.event_bus = (
            event_bus
        )
        self.system_mode_manager = system_mode_manager or SystemModeManager()

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

        self.interaction_outcome_tracker = (
            interaction_outcome_tracker
        )

        self.fusion_window = (
            fusion_window
        )

        self._pending_events = []
        self._pending_generations = {}

        self._lock = (
            threading.RLock()
        )

        self._timer = None
        self._stopped = False
        self._stop_complete = False
        self._stop_thread = None
        self._active_flush_threads = []
        self._condition = threading.Condition(self._lock)

        # Publish only after all synchronization state is initialized.
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

        # Do not wait for the admission barrier after shutdown has begun.
        with self._lock:
            if self._stopped:
                return

        generation = self.system_mode_manager.generation
        if not self._is_system_control(event):
            with self.system_mode_manager.processing(event.timestamp) as active:
                if not active:
                    return
                generation = self.system_mode_manager.generation

        with self._lock:

            if self._stopped:
                return

            if self._is_system_control(event) and event.payload['command'] == 'zero ui suspender':
                self._pending_events.clear()
                self._pending_generations.clear()

            self._pending_events.append(
                event
            )
            self._pending_generations[id(event)] = generation

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

    def _record_action_outcome(
        self,
        action,
        success
    ):
        """
        Registra el resultado técnico
        de una acción.
    
        Un fallo del tracker nunca debe
        detener la interacción principal.
        """
    
        if (
            self.interaction_outcome_tracker
            is None
        ):
            return
    
        try:
        
            self.interaction_outcome_tracker \
                .record_action_result(
                    action,
                    success
                )
    
        except Exception as error:
        
            print(
                "ERROR RESULTADO INTERACCION: "
                f"{type(error).__name__}: "
                f"{error}"
            )
    
    
    def _record_cursor_outcome(
        self,
        event
    ):
        """
        Registra el patrón de movimiento
        ejecutado por el cursor.
        """
    
        if (
            self.interaction_outcome_tracker
            is None
        ):
            return
    
        try:
        
            self.interaction_outcome_tracker \
                .record_cursor_event(
                    event
                )
    
        except Exception as error:
        
            print(
                "ERROR RESULTADO CURSOR: "
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
            if self._stopped:
                return
        batch_generation = self.system_mode_manager.generation
        thread_id = threading.get_ident()
        with self._condition:
            if self._stopped:
                return

            events = list(self._pending_events)
            generations = self._pending_generations.copy()
            self._pending_events.clear()
            self._pending_generations.clear()
            self._timer = None
            if not events:
                return

            self._active_flush_threads.append(thread_id)

        try:
            controls = [event for event in events if self._is_system_control(event)]
            for event in controls:
                with self._lock:
                    if self._stopped:
                        return
                self._execute_system_control(
                    event, generations.get(id(event), batch_generation),
                )

            admitted = []
            for event in events:
                if self._is_system_control(event):
                    continue
                with self.system_mode_manager.processing(
                    event.timestamp, generations.get(id(event), batch_generation),
                ) as active:
                    if active:
                        admitted.append(event)
            resolved_events = self.fusion_engine.process_events(admitted) if admitted else []

            for event in resolved_events:
                with self._lock:
                    if self._stopped:
                        break

                with self.system_mode_manager.processing(
                    event.timestamp, generations.get(id(event), batch_generation),
                ) as active:
                    if not active:
                        continue
                    self._record_session_event(event)
                    try:
                        self._execute_event(event)
                    except Exception as error:
                        print(
                            "ERROR MULTIMODAL: "
                            f"{type(error).__name__}: {error}"
                        )
                        self._show_error_feedback("No se pudo ejecutar la acción")
        finally:
            # Includes fusion, execution, outcomes and feedback failures.
            with self._condition:
                self._active_flush_threads.remove(thread_id)
                self._condition.notify_all()

    @staticmethod
    def _is_system_control(event):
        return (
            event.source == EventSource.SYSTEM
            and event.event_type == EventType.STATUS
            and event.payload.get('level') == 'system_control'
            and event.payload.get('command') in SYSTEM_CONTROL_COMMANDS
        )

    def _execute_system_control(self, event, generation=None):
        command = event.payload['command']
        with self.system_mode_manager.processing(event.timestamp, generation) as active:
            if not active and command not in ('zero ui activar', 'zero ui suspender'):
                return
            try:
                if self.overlay_service is not None:
                    if command == 'zero ui mostrar comandos':
                        self.overlay_service.show_commands()
                    elif command == 'zero ui ocultar comandos':
                        self.overlay_service.hide_commands()
                self._show_feedback(SYSTEM_CONTROL_COMMANDS[command], 'system_control')
            except Exception:
                pass

    def _show_feedback(
        self,
        text,
        feedback_type="success"
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

        try:
            self.overlay_service.show_feedback(text, feedback_type=feedback_type)
        except Exception:
            # Visual feedback must not interrupt command execution.
            pass

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
    
        try:
            self.overlay_service.show_error_feedback(text)
        except Exception:
            pass

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
        with self.system_mode_manager.processing(event.timestamp) as active:
            if active:
                self._execute_active_event(event)

    def _execute_active_event(
        self,
        event
    ):
        """
        Ejecuta el evento aprobado
        por FusionEngine.
        """

        with self._lock:
            if self._stopped:
                return

        if (
            event.event_type
            == EventType.ACTION
        ):

            if event.action is None:
                return

            mode_feedback = (
                "success" if event.source == EventSource.GESTURE else "mode"
            )

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
                        "Dibujo activado", feedback_type=mode_feedback
                    )

                else:

                    self._show_feedback(
                        "Dibujo desactivado", feedback_type=mode_feedback
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
                    "Borrador activado", feedback_type=mode_feedback
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
                    "Borrador desactivado", feedback_type=mode_feedback
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
                        "Borrador activado", feedback_type=mode_feedback
                    )

                else:

                    self._show_feedback(
                        "Borrador desactivado", feedback_type=mode_feedback
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

            try:

                success = (
                    self.action_executor
                    .execute(
                        event.action
                    )
                )

            except Exception:
            
                self._record_action_outcome(
                    event.action,
                    False
                )

                raise
            
            
            success = bool(
                success
            )

            self._record_action_outcome(
                event.action,
                success
            )


            if not success:
            
                self._show_error_feedback(
                    "Acción no ejecutada"
                )

                return


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
                level in ("success", "mode")
                and message
            ):
        
                self._show_feedback(
                    message, feedback_type=level
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

                result = (
                    self.mouse.move_relative(
                        dx,
                        dy
                    )
                )

                if result is not False:
                
                    self._record_cursor_outcome(
                        event
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

                    result = (
                        self.mouse.move_to(
                            x,
                            y
                        )
                    )

                    if result is not False:
                    
                        self._record_cursor_outcome(
                            event
                        )

    def stop(self):
        """Reject new events and wait for active batches before finalizing.

        Must be called outside a flush callback: a worker cannot wait for
        its own execution to finish.
        """
        thread_id = threading.get_ident()
        with self._condition:
            if (
                thread_id in self._active_flush_threads
                or thread_id == self._stop_thread
            ):
                raise RuntimeError(
                    "stop() no puede ejecutarse desde un callback activo "
                    "del coordinador."
                )

            if self._stopped:
                self._condition.wait_for(lambda: self._stop_complete)
                return

            self._stopped = True
            self._stop_thread = thread_id
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            self._pending_events.clear()
            self._pending_generations.clear()

        try:
            # Do not hold the coordinator lock while calling the EventBus.
            try:
                self.event_bus.unsubscribe_all(self._receive_event)
            except Exception as error:
                # The stopped guard also rejects callbacks already copied
                # by EventBus.publish() before unsubscription.
                print(
                    "ERROR DESUSCRIPCION MULTIMODAL: "
                    f"{type(error).__name__}: {error}"
                )

            with self._condition:
                self._condition.wait_for(
                    lambda: not self._active_flush_threads
                )

            if self.interaction_outcome_tracker is not None:
                try:
                    self.interaction_outcome_tracker.finalize_pending_drag()
                except Exception as error:
                    print(
                        "ERROR CIERRE INTERACCION: "
                        f"{type(error).__name__}: {error}"
                    )
        finally:
            with self._condition:
                self._stop_complete = True
                self._stop_thread = None
                self._condition.notify_all()
