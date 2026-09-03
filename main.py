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

    voice_service = (
        VoiceControlService(
            mouse_controller,
            profile
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