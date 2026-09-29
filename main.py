from application.calibration.calibration_service import (
    CalibrationService
)

from application.interaction.head_control_service import (
    HeadControlService
)

from application.interaction.voice_control_service import (
    VoiceControlService
)

from infrastructure.windows.mouse_controller import (
    MouseController
)

from application.interaction.action_executor import (
    ActionExecutor
)

from infrastructure.windows.keyboard_controller import (
    KeyboardController
)

from modules.voice.voice_mode import (
    VoiceModeManager
)

from modules.voice.dictation_recognizer import (
    DictationRecognizer
)

from application.interaction.dictation_service import (
    DictationService
)

from infrastructure.windows.text_input_controller import (
    TextInputController
)


def main():

    print("")
    print("==============================")
    print("          ZEROUI-AC")
    print("          SPRINT 1")
    print("==============================")
    print("")

    calibration_service = (
        CalibrationService()
    )

    profile = (
        calibration_service.get_profile()
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
            action_executor=(
                action_executor
            ),
            calibration_profile=(
                profile
            ),
            dictation_service=(
                dictation_service
            ),
            voice_mode_manager=(
                voice_mode_manager
            )
        )
    )

    head_service = (
        HeadControlService(
            mouse_controller,
            calibration_service
        )
    )

    try:
        voice_service.start()
        head_service.run()
    
    except KeyboardInterrupt:
        print("")
        print("Interrupción solicitada por el usuario.")
    
    finally:
        voice_service.stop()
    
        print("")
        print("ZeroUI-AC finalizado.")

if __name__ == "__main__":
    main()