from application.calibration.calibration_service import (
    CalibrationService
)

from application.interaction.voice_control_service import (
    VoiceControlService
)

from application.interaction.action_executor import (
    ActionExecutor
)

from application.interaction.dictation_service import (
    DictationService
)

from application.interaction.multimodal_coordinator import (
    MultimodalCoordinator
)

from application.interaction.multimodal_vision_service import (
    MultimodalVisionService
)

from application.interaction.zoom_service import (
    ZoomService
)

from infrastructure.windows.mouse_controller import (
    MouseController
)

from infrastructure.windows.keyboard_controller import (
    KeyboardController
)

from infrastructure.windows.text_input_controller import (
    TextInputController
)

from infrastructure.windows.magnification_controller import (
    MagnificationController
)

from infrastructure.windows.audio_feedback_service import (
    AudioFeedbackService
)

from infrastructure.event_bus.event_bus import (
    EventBus
)

from modules.multimodal.fusion_engine import (
    FusionEngine
)

from modules.adaptation.session_manager import (
    SessionManager
)

from modules.adaptation.session_persistence import (
    SessionPersistence
)

from modules.adaptation.adaptive_parameters import (
    AdaptiveParametersManager
)

from modules.adaptation.adaptive_channel_weights import (
    AdaptiveChannelWeights
)

from modules.adaptation.adaptive_action_applier import (
    AdaptiveActionApplier
)

from modules.adaptation.adaptive_runtime_controller import (
    AdaptiveRuntimeController
)

from modules.adaptation.q_learning_agent import (
    QLearningAgent
)

from modules.adaptation.q_learning_persistence import (
    QLearningPersistence
)

from modules.voice.voice_mode import (
    VoiceModeManager
)

from modules.voice.dictation_recognizer import (
    DictationRecognizer
)

from presentation.overlay.annotation_overlay import (
    AnnotationOverlay
)

from application.interaction.zoom_mode_manager import (
    ZoomModeManager
)
from application.interaction.system_mode_manager import SystemModeManager

from modules.adaptation.interaction_outcome_tracker import (
    InteractionOutcomeTracker
)

from application.facade import ZeroUIApplicationFacade
from presentation.api import create_app
from presentation.api.server import LocalApiServer
from presentation.overlay.command_help import get_command_catalog

def print_session_summary(
    summary
):
    """
    Muestra un resumen final
    de una sesión de ZeroUI-AC.
    """

    if summary is None:
        return

    metrics = (
        summary.get(
            "metrics",
            {}
        )
    )

    fatigue = (
        summary.get(
            "fatigue",
            {}
        )
        or {}
    )

    source_counts = (
        metrics.get(
            "source_counts",
            {}
        )
    )

    duration = (
        metrics.get(
            "duration_seconds",
            0.0
        )
    )

    error_rate = (
        metrics.get(
            "error_rate",
            0.0
        )
        * 100
    )

    print("")
    print("==============================")
    print("       RESUMEN DE SESION")
    print("==============================")

    print(
        "ID: "
        f"{summary.get('session_id')}"
    )

    print(
        "Duracion: "
        f"{duration:.1f} segundos"
    )

    print(
        "Eventos: "
        f"{metrics.get('total_events', 0)}"
    )

    print(
        "Acciones: "
        f"{metrics.get('action_events', 0)}"
    )

    print(
        "Movimientos de cursor: "
        f"{metrics.get('cursor_events', 0)}"
    )

    print(
        "Errores: "
        f"{metrics.get('error_events', 0)}"
    )

    print(
        "Tasa de error: "
        f"{error_rate:.2f}%"
    )

    print(
        "Cambios de canal: "
        f"{metrics.get('channel_switches', 0)}"
    )

    fatigue_score = (
        fatigue.get(
            "score"
        )
    )

    fatigue_level = (
        fatigue.get(
            "level",
            "unavailable"
        )
    )

    if fatigue_score is None:

        print(
            "Fatiga operativa: "
            "no disponible"
        )

    else:

        print(
            "Fatiga operativa: "
            f"{fatigue_level} "
            f"({fatigue_score:.2f})"
        )

    print("")
    print("EVENTOS POR CANAL")

    print(
        "Voz: "
        f"{source_counts.get('voice', 0)}"
    )

    print(
        "Cabeza: "
        f"{source_counts.get('head', 0)}"
    )

    print(
        "Extremidad: "
        f"{source_counts.get('limb', 0)}"
    )

    print(
        "Gestos: "
        f"{source_counts.get('gesture', 0)}"
    )

    print(
        "Sistema: "
        f"{source_counts.get('system', 0)}"
    )

    print("==============================")
    print("")

def print_adaptation_summary(result):
    """Console observer; all values come from the completed runtime step."""
    def number(value, digits=2):
        return "no disponible" if value is None else f"{value:.{digits}f}"

    def transition(before, after, attribute):
        return (
            f"{number(getattr(before, attribute, None))} -> "
            f"{number(getattr(after, attribute, None))}"
        )

    state_labels = (
        "Error voz", "Actividad", "Cambios de canal",
        "Canal dominante", "Etapa sesión",
    )
    reward = (
        "pendiente (primera adaptación)"
        if result.reward is None else number(result.reward, 3)
    )
    lines = ["", "[ADAPTACIÓN]", f"state_key: {result.state_key}", "Estado:"]
    lines.extend(
        f"  {label}: {value}"
        for label, value in zip(state_labels, result.state_key)
    )
    lines.extend([
        "Resultados ventana:",
        f"  Fallos acciones: {number(result.action_failure_rate)}",
        f"  Fallos arrastre: {number(result.drag_failure_rate)}",
        f"  Correcciones cursor: {number(result.correction_rate)}",
        f"  Fatiga: {number(result.fatigue_score)}",
        "Q-learning:",
        f"  Recompensa: {reward}",
        f"  Acción elegida: {result.action.name}",
        f"  Cambio aplicado: {'Sí' if result.changed else 'No'}",
        "Parámetros:",
    ])
    for label, attribute in (
        ("Cabeza", "head_sensitivity_factor"),
        ("Extremidad", "limb_sensitivity_factor"),
    ):
        lines.append(
            f"  {label}: "
            + transition(result.parameters_before, result.parameters_after, attribute)
        )
    lines.append("Pesos:")
    for label, attribute in (
        ("Voz", "voice"), ("Cabeza", "head"),
        ("Extremidad", "limb"), ("Gestos", "gesture"),
    ):
        lines.append(
            f"  {label}: "
            + transition(result.weights_before, result.weights_after, attribute)
        )
    lines.append(f"Epsilon: {number(result.epsilon, 4)}")
    # One print reduces interleaving with other console producers.
    print("\n".join(lines))


def build_local_api(
    *,
    system_mode_manager,
    session_manager,
    adaptive_parameters_manager,
    adaptive_channel_weights,
    q_learning_agent,
    voice_mode_manager,
    zoom_mode_manager,
    commands_presenter,
    adaptive_runtime,
):
    """Compose the API facade from the exact instances used by the motor."""
    facade = ZeroUIApplicationFacade(
        system_mode_manager=system_mode_manager,
        session_manager=session_manager,
        adaptive_parameters_manager=adaptive_parameters_manager,
        adaptive_channel_weights=adaptive_channel_weights,
        q_learning_agent=q_learning_agent,
        voice_mode_manager=voice_mode_manager,
        zoom_mode_manager=zoom_mode_manager,
        commands_presenter=commands_presenter,
        command_catalog_provider=get_command_catalog,
        adaptive_runtime=adaptive_runtime,
    )
    return facade, create_app(facade)


def warn_api_unavailable():
    print("ADVERTENCIA: API local no disponible.")


def main():

    print("")
    print("==============================")
    print("          ZEROUI-AC")
    print("          SPRINT 4")
    print("==============================")
    print("")

    calibration_service = (
        CalibrationService()
    )

    profile = (
        calibration_service
        .get_profile()
    )

    mouse_controller = (
        MouseController()
    )

    magnification_controller = (
        MagnificationController()
    )

    zoom_service = (
        ZoomService(
            magnification_controller=(
                magnification_controller
            ),
            mouse_controller=(
                mouse_controller
            )
        )
    )

    keyboard_controller = (
        KeyboardController()
    )

    action_executor = (
        ActionExecutor(
            mouse_controller,
            keyboard_controller
        )
    )

    system_mode_manager = SystemModeManager()

    overlay_service = (
        AnnotationOverlay(system_mode_manager=system_mode_manager)
    )

    overlay_service.start()

    audio_feedback_service = (
        AudioFeedbackService(
            enabled=True
        )
    )

    event_bus = (
        EventBus()
    )

    # ---------------------------------
    # Sprint 4 - Adaptación
    # ---------------------------------

    adaptive_parameters_manager = (
        AdaptiveParametersManager()
    )

    adaptive_channel_weights = (
        AdaptiveChannelWeights()
    )

    adaptive_action_applier = (
        AdaptiveActionApplier(
            parameters_manager=(
                adaptive_parameters_manager
            ),
            channel_weights=(
                adaptive_channel_weights
            )
        )
    )

    q_learning_agent = (
        QLearningAgent(
            learning_rate=0.20,
            discount_factor=0.90,
            epsilon=0.10,
            epsilon_min=0.02,
            epsilon_decay=0.995
        )
    )

    q_learning_persistence = (
        QLearningPersistence()
    )

    try:

        learning_loaded = (
            q_learning_persistence
            .load(
                q_learning_agent
            )
        )

        if learning_loaded:

            print(
                "Aprendizaje Q-learning "
                "recuperado."
            )

        else:

            print(
                "No existe aprendizaje "
                "Q-learning previo."
            )

    except ValueError as error:

        print(
            "ADVERTENCIA Q-LEARNING: "
            f"{error}"
        )

    session_persistence = (
        SessionPersistence(
            base_directory=(
                "data/sessions"
            )
        )
    )

    fusion_engine = (
        FusionEngine(
            channel_weights=(
                adaptive_channel_weights
            )
        )
    )

    session_manager = (
        SessionManager(
            persistence=(
                session_persistence
            )
        )
    )

    interaction_outcome_tracker = (
        InteractionOutcomeTracker()
    )

    adaptive_runtime = (
        AdaptiveRuntimeController(
            system_mode_manager=system_mode_manager,
            session_manager=(
                session_manager
            ),
            action_applier=(
                adaptive_action_applier
            ),
            q_agent=(
                q_learning_agent
            ),
            interaction_outcome_tracker=(
                interaction_outcome_tracker
            ),

            # Nunca se adapta por frame.
            adaptation_interval_seconds=30.0,

            # El hilo solo consulta una vez
            # por segundo si corresponde.
            worker_poll_seconds=1.0,

            min_user_events=5,
            on_adaptation=print_adaptation_summary,
        )
    )

    multimodal_coordinator = (
        MultimodalCoordinator(
            system_mode_manager=system_mode_manager,
            event_bus=event_bus,
            fusion_engine=(
                fusion_engine
            ),
            action_executor=(
                action_executor
            ),
            mouse_controller=(
                mouse_controller
            ),
            overlay_service=(
                overlay_service
            ),
            zoom_service=(
                zoom_service
            ),
            audio_feedback_service=(
                audio_feedback_service
            ),
            session_manager=(
                session_manager
            ),

            interaction_outcome_tracker=(
                interaction_outcome_tracker
            )
        )
    )

    voice_mode_manager = (
        VoiceModeManager()
    )

    zoom_mode_manager = (
        ZoomModeManager()
    )

    try:

        dictation_recognizer = (
            DictationRecognizer(
                sample_rate=(
                    profile
                    .microphone_sample_rate
                )
            )
        )

    except FileNotFoundError as error:

        print("")
        print(
            "ERROR DE DICTADO:"
        )

        print(
            error
        )

        multimodal_coordinator.stop()

        overlay_service.stop()

        zoom_service.close()

        return

    text_input_controller = (
        TextInputController()
    )

    dictation_service = (
        DictationService(
            recognizer=(
                dictation_recognizer
            ),
            text_input_controller=(
                text_input_controller
            ),
            voice_mode_manager=(
                voice_mode_manager
            )
        )
    )

    voice_service = (
        VoiceControlService(
            system_mode_manager=system_mode_manager,
            event_bus=event_bus,
            calibration_profile=profile,
            dictation_service=(
                dictation_service
            ),
            voice_mode_manager=(
                voice_mode_manager
            ),
            zoom_mode_manager=(
                zoom_mode_manager
            )
        )
    )

    vision_service = (
        MultimodalVisionService(
            system_mode_manager=system_mode_manager,
            event_bus=event_bus,

            mouse_controller=(
                mouse_controller
            ),

            calibration_service=(
                calibration_service
            ),

            zoom_mode_manager=(
                zoom_mode_manager
            ),

            adaptive_parameters_manager=(
                adaptive_parameters_manager
            )
        )
    )

    api_server = None
    try:
        api_facade, api_app = build_local_api(
            system_mode_manager=system_mode_manager,
            session_manager=session_manager,
            adaptive_parameters_manager=adaptive_parameters_manager,
            adaptive_channel_weights=adaptive_channel_weights,
            q_learning_agent=q_learning_agent,
            voice_mode_manager=voice_mode_manager,
            zoom_mode_manager=zoom_mode_manager,
            commands_presenter=overlay_service,
            adaptive_runtime=adaptive_runtime,
        )
        api_server = LocalApiServer(
            api_app,
            on_error=warn_api_unavailable,
        )
    except Exception:
        warn_api_unavailable()

    session_id = (
        session_manager
        .start_session()
    )

    print("")
    print(
        "Sesion iniciada: "
        f"{session_id}"
    )
    print("")

    adaptive_started = (
        adaptive_runtime.start()
    )

    if adaptive_started:

        print(
            "Adaptacion inteligente: "
            "ACTIVA"
        )

        print(
            "Intervalo adaptativo: "
            "30 segundos"
        )

    else:

        print(
            "ADVERTENCIA: "
            "no se pudo iniciar "
            "la adaptacion."
        )

    print("")

    if api_server is not None:
        try:
            api_server.start()
        except Exception:
            try:
                api_server.stop()
            except Exception:
                pass
            api_server = None
            warn_api_unavailable()

    try:

        voice_service.start()

        vision_service.run()

    except KeyboardInterrupt:

        print("")
        print(
            "Interrupción solicitada "
            "por el usuario."
        )

    finally:

        # Stop HTTP access before any dependency used by the facade is closed.
        if api_server is not None:
            try:
                api_server.stop()
            except Exception:
                warn_api_unavailable()

        voice_service.stop()

        # Primero se detienen nuevos
        # eventos y ejecuciones.
        multimodal_coordinator.stop()

        # Seguridad:
        # ZeroUI nunca debe finalizar
        # dejando el botón izquierdo
        # físicamente presionado.
        mouse_controller.stop_drag()

        # Después Q-learning aprende
        # del último intervalo mientras
        # la sesión todavía está activa.
        adaptive_runtime.stop()

        try:

            q_learning_persistence.save(
                q_learning_agent
            )
        
            print(
                "Aprendizaje Q-learning "
                "guardado."
            )
        
        except Exception as error:
        
            print(
                "ADVERTENCIA AL GUARDAR "
                "Q-LEARNING: "
                f"{type(error).__name__}: "
                f"{error}"
            )

        session_summary = (
            session_manager.end_session()
        )

        q_table_snapshot = (
            q_learning_agent
            .get_q_table_snapshot()
        )
        
        print(
            "Estados Q aprendidos: "
            f"{len(q_table_snapshot)}"
        )
        
        print(
            "Epsilon actual: "
            f"{q_learning_agent.epsilon:.4f}"
        )
    
        print_session_summary(
            session_summary
        )

        outcome_summary = (
            interaction_outcome_tracker
            .snapshot()
        )

        print("")
        print("==============================")
        print("   RESULTADOS INTERACCION")
        print("==============================")

        print(
            "Acciones intentadas: "
            f"{outcome_summary['action_attempts']}"
        )

        print(
            "Acciones correctas: "
            f"{outcome_summary['action_successes']}"
        )

        print(
            "Acciones fallidas: "
            f"{outcome_summary['action_failures']}"
        )

        print(
            "Tasa exito acciones: "
            f"{outcome_summary['action_success_rate'] * 100:.2f}%"
        )

        print(
            "Arrastres intentados: "
            f"{outcome_summary['drag_attempts']}"
        )

        print(
            "Arrastres correctos: "
            f"{outcome_summary['drag_successes']}"
        )

        print(
            "Arrastres fallidos: "
            f"{outcome_summary['drag_failures']}"
        )

        print(
            "Tasa exito arrastre: "
            f"{outcome_summary['drag_success_rate'] * 100:.2f}%"
        )

        print(
            "Muestras cursor: "
            f"{outcome_summary['cursor_samples']}"
        )

        print(
            "Correcciones detectadas: "
            f"{outcome_summary['correction_events']}"
        )

        print(
            "Tasa correcciones: "
            f"{outcome_summary['correction_rate'] * 100:.2f}%"
        )

        print("==============================")
        print("")

        adaptive_parameters = (
            adaptive_parameters_manager
            .snapshot()
        )

        adaptive_weights = (
            adaptive_channel_weights
            .snapshot()
        )

        print("")
        print("==============================")
        print("      ESTADO ADAPTATIVO")
        print("==============================")

        print(
            "Sensibilidad cabeza: "
            f"{adaptive_parameters.head_sensitivity_factor:.2f}"
        )

        print(
            "Sensibilidad extremidad: "
            f"{adaptive_parameters.limb_sensitivity_factor:.2f}"
        )

        print(
            "Peso voz: "
            f"{adaptive_weights.voice:.2f}"
        )

        print(
            "Peso cabeza: "
            f"{adaptive_weights.head:.2f}"
        )

        print(
            "Peso extremidad: "
            f"{adaptive_weights.limb:.2f}"
        )

        print(
            "Peso gestos: "
            f"{adaptive_weights.gesture:.2f}"
        )

        last_reward = (
            adaptive_runtime
            .get_last_reward()
        )

        if last_reward is not None:

            print(
                "Ultima recompensa RL: "
                f"{last_reward:.3f}"
            )

        adaptation_error = (
            adaptive_runtime
            .get_last_error()
        )

        if adaptation_error:

            print(
                "Advertencia adaptativa: "
                f"{adaptation_error}"
            )

        persistence_error = (
            session_manager
            .get_last_persistence_error()
        )

        if persistence_error:

            print(
                "Advertencia persistencia: "
                f"{persistence_error}"
            )

        print("==============================")
        print("")
    
        zoom_service.close()
    
        overlay_service.stop()
    
        print("")
        print(
            "ZeroUI-AC finalizado."
        )


if __name__ == "__main__":
    main()
