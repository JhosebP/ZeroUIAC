from unittest.mock import Mock

import main


def test_api_composition_injects_motor_instances_into_one_facade(monkeypatch):
    dependencies = {
        "system_mode_manager": object(),
        "session_manager": object(),
        "adaptive_parameters_manager": object(),
        "adaptive_channel_weights": object(),
        "q_learning_agent": object(),
        "voice_mode_manager": object(),
        "zoom_mode_manager": object(),
        "commands_presenter": object(),
        "adaptive_runtime": object(),
    }
    facade = object()
    app = object()
    facade_factory = Mock(return_value=facade)
    app_factory = Mock(return_value=app)
    agent_factory = Mock(side_effect=AssertionError("must reuse existing Q agent"))
    monkeypatch.setattr(main, "ZeroUIApplicationFacade", facade_factory)
    monkeypatch.setattr(main, "create_app", app_factory)
    monkeypatch.setattr(main, "QLearningAgent", agent_factory)

    actual_facade, actual_app = main.build_local_api(**dependencies)

    assert actual_facade is facade
    assert actual_app is app
    facade_factory.assert_called_once_with(
        **dependencies,
        command_catalog_provider=main.get_command_catalog,
    )
    app_factory.assert_called_once_with(facade)
    agent_factory.assert_not_called()
