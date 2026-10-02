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

from infrastructure.windows.mouse_controller import (
    MouseController
)

from infrastructure.windows.keyboard_controller import (
    KeyboardController
)

from infrastructure.windows.text_input_controller import (
    TextInputController
)

from infrastructure.event_bus.event_bus import (
    EventBus
)

from modules.multimodal.fusion_engine import (
    FusionEngine
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

def main():

    print("")
    print("==============================")
    print("          ZEROUI-AC")
    print("          SPRINT 3")
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

    event_bus = (
        EventBus()
    )

    fusion_engine = (
        FusionEngine()
    )

    multimodal_coordinator = (
        MultimodalCoordinator(
            event_bus=event_bus,
            fusion_engine=fusion_engine,
            action_executor=action_executor,
            mouse_controller=(
                mouse_controller
            ),
            overlay_service=(
                overlay_service
            )
        )
    )

    voice_mode_manager = (
        VoiceModeManager()
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
        print(error)

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
            )
        )
    )

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

        overlay_service.stop()

        print("")
        print(
            "ZeroUI-AC finalizado."
        )


if __name__ == "__main__":
    main()