from copy import deepcopy


class ZeroUIApplicationFacade:
    """Read-only queries and delegation over injected, existing services.

    command_catalog_provider is a zero-argument callable returning the
    modes/execution/system/gestures catalog shared with the commands panel.
    Component snapshots are not a global transaction over the entire engine.
    The shared system barrier keeps adaptive reads consistent with runtime
    steps and keeps active/suspended complementary during status queries.
    """

    def __init__(
        self,
        *,
        system_mode_manager,
        session_manager,
        adaptive_parameters_manager,
        adaptive_channel_weights,
        q_learning_agent,
        voice_mode_manager,
        zoom_mode_manager,
        commands_presenter,
        command_catalog_provider,
        adaptive_runtime=None,
    ):
        self._system_mode_manager = system_mode_manager
        self._session_manager = session_manager
        self._adaptive_parameters_manager = adaptive_parameters_manager
        self._adaptive_channel_weights = adaptive_channel_weights
        self._q_learning_agent = q_learning_agent
        self._voice_mode_manager = voice_mode_manager
        self._zoom_mode_manager = zoom_mode_manager
        self._commands_presenter = commands_presenter
        self._command_catalog_provider = command_catalog_provider
        self._adaptive_runtime = adaptive_runtime

    def _system_activity(self):
        suspended = self._system_mode_manager.is_suspended()
        return {"active": not suspended, "suspended": suspended}

    def get_system_status(self):
        with self._system_mode_manager.processing():
            return {
                **self._system_activity(),
                "voice_mode": self._voice_mode_manager.mode.value,
                "zoom_enabled": self._zoom_mode_manager.is_enabled(),
                "commands_visible": self._commands_presenter.commands_visible,
            }

    def get_session_metrics(self):
        # One session snapshot avoids racing separate is_active/id reads.
        snapshot = self._session_manager.get_snapshot()
        if snapshot is None:
            return {"session_active": False}
        return {
            "session_active": True,
            "session_id": snapshot["session_id"],
            "started_at": snapshot["started_at"],
            **deepcopy(snapshot["metrics"]),
        }

    def get_adaptation_state(self):
        with self._system_mode_manager.processing():
            parameters = self._adaptive_parameters_manager.snapshot()
            weights = self._adaptive_channel_weights.snapshot()
            result = {
                "head_sensitivity_factor": parameters.head_sensitivity_factor,
                "limb_sensitivity_factor": parameters.limb_sensitivity_factor,
                "weights": deepcopy(weights.as_dict()),
                "epsilon": self._q_learning_agent.epsilon,
                "q_states": len(self._q_learning_agent.get_q_table_snapshot()),
            }
            if self._adaptive_runtime is not None:
                result["last_reward"] = self._adaptive_runtime.get_last_reward()
            return result

    def get_commands(self):
        return deepcopy(self._command_catalog_provider())

    def suspend(self):
        with self._system_mode_manager.processing():
            self._system_mode_manager.suspend()
            return {"success": True, **self._system_activity()}

    def activate(self):
        with self._system_mode_manager.processing():
            self._system_mode_manager.activate()
            return {"success": True, **self._system_activity()}

    def show_commands(self):
        self._commands_presenter.show_commands()
        return {
            "success": True,
            "commands_visible": self._commands_presenter.commands_visible,
        }

    def hide_commands(self):
        self._commands_presenter.hide_commands()
        return {
            "success": True,
            "commands_visible": self._commands_presenter.commands_visible,
        }
