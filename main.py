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

def print_session_summary(
    summary
):
    """
    Muestra un resumen temporal de
    la sesión actual.

    La persistencia JSON se implementará
    posteriormente.
    """

    if summary is None:
        return

    metrics = (
        summary.get(
            "metrics",
            {}
        )
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

    overlay_service = (
        AnnotationOverlay()
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

    fusion_engine = (
        FusionEngine()
    )

    session_manager = (
        SessionManager()
    )

    multimodal_coordinator = (
        MultimodalCoordinator(
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
            event_bus=event_bus,
            mouse_controller=(
                mouse_controller
            ),
            calibration_service=(
                calibration_service
            ),
            zoom_mode_manager=(
                zoom_mode_manager
            )
        )
    )

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

        voice_service.stop()
    
        multimodal_coordinator.stop()
    
        session_summary = (
            session_manager
            .end_session()
        )
    
        print_session_summary(
            session_summary
        )
    
        zoom_service.close()
    
        overlay_service.stop()
    
        print("")
        print(
            "ZeroUI-AC finalizado."
        )


if __name__ == "__main__":
    main()