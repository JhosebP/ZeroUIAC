import uvicorn

from presentation.api.app import create_app


class DevelopmentFacade:
    def __init__(self):
        self.suspended = False
        self.commands_visible = False

    def get_system_status(self):
        return {
            "active": not self.suspended,
            "suspended": self.suspended,
            "voice_mode": "command",
            "zoom_enabled": False,
            "commands_visible": self.commands_visible,
        }

    def get_session_metrics(self):
        return {
            "session_active": True,
            "session_id": "development-session",
            "duration_seconds": 120.0,
            "total_events": 350,
            "action_events": 20,
            "cursor_events": 330,
            "error_events": 0,
            "error_rate": 0.0,
            "channel_switches": 8,
            "source_counts": {
                "voice": 20,
                "head": 250,
                "limb": 80,
                "gesture": 0,
                "system": 0,
            },
        }

    def get_adaptation_state(self):
        return {
            "head_sensitivity_factor": 1.0,
            "limb_sensitivity_factor": 1.0,
            "weights": {
                "voice": 1.0,
                "head": 1.0,
                "limb": 1.0,
                "gesture": 1.0,
            },
            "epsilon": 0.0588,
            "q_states": 15,
            "last_reward": 0.65,
        }

    def get_commands(self):
        return {
            "modes": [
                "activar dictado",
                "activar zoom",
                "desactivar zoom",
            ],
            "execution": [
                "clic",
                "doble clic",
                "copiar",
                "pegar",
                "enter",
            ],
            "system": [
                "zero ui suspender",
                "zero ui activar",
                "zero ui mostrar comandos",
                "zero ui ocultar comandos",
            ],
            "gestures": [
                "Mover cabeza: controlar cursor",
                "Adelante: acercar",
                "Atrás: alejar",
            ],
        }

    def suspend(self):
        self.suspended = True

        return {
            "success": True,
            "active": False,
            "suspended": True,
        }

    def activate(self):
        self.suspended = False

        return {
            "success": True,
            "active": True,
            "suspended": False,
        }

    def show_commands(self):
        self.commands_visible = True

        return {
            "success": True,
            "commands_visible": True,
        }

    def hide_commands(self):
        self.commands_visible = False

        return {
            "success": True,
            "commands_visible": False,
        }


facade = DevelopmentFacade()

app = create_app(facade)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8765,
        log_level="warning",
    )