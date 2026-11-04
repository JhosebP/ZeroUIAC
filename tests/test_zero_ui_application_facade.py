import json
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from application.facade import ZeroUIApplicationFacade
from application.interaction.system_mode_manager import SystemModeManager
from application.interaction.zoom_mode_manager import ZoomModeManager
from domain.events.event_types import EventSource
from modules.adaptation.adaptive_actions import AdaptiveAction
from modules.adaptation.adaptive_channel_weights import AdaptiveChannelWeights
from modules.adaptation.adaptive_parameters import AdaptiveParametersManager
from modules.adaptation.q_learning_agent import QLearningAgent
from modules.voice.voice_commands import SYSTEM_CONTROL_COMMANDS, VOICE_COMMANDS
from modules.voice.voice_mode import VoiceMode, VoiceModeManager
from presentation.overlay.command_help import get_command_catalog, get_command_groups


class FakeCommandsPresenter:
    def __init__(self):
        self.commands_visible = False
        self.panels_created = 0
        self.show_calls = 0
        self.hide_calls = 0

    def show_commands(self):
        self.show_calls += 1
        if not self.commands_visible:
            self.commands_visible = True
            self.panels_created += 1

    def hide_commands(self):
        self.hide_calls += 1
        self.commands_visible = False


@pytest.fixture
def dependencies():
    snapshot = {
        'session_id': 'session-test',
        'started_at': '2026-10-26T12:00:00+00:00',
        'metrics': {
            'duration_seconds': 120.5,
            'total_events': 500,
            'action_events': 15,
            'cursor_events': 480,
            'error_events': 1,
            'error_rate': 0.002,
            'channel_switches': 12,
            'source_counts': {
                'voice': 15, 'head': 430, 'limb': 50, 'gesture': 5, 'system': 0,
            },
        },
    }
    parameters = AdaptiveParametersManager()
    parameters.apply(AdaptiveAction.INCREASE_HEAD_SENSITIVITY)
    parameters.apply(AdaptiveAction.DECREASE_LIMB_SENSITIVITY)
    weights = AdaptiveChannelWeights()
    weights.increase(EventSource.VOICE)
    agent = QLearningAgent(epsilon=0.0631, seed=1)
    agent.set_q_value(('low', 'high', 'low', 'head', 'short'), AdaptiveAction.NO_CHANGE, 0.5)
    agent.set_q_value(('low', 'low', 'low', 'mixed', 'short'), AdaptiveAction.NO_CHANGE, 0.1)
    return {
        'system_mode_manager': SystemModeManager(),
        'session_manager': SimpleNamespace(get_snapshot=Mock(return_value=snapshot)),
        'adaptive_parameters_manager': parameters,
        'adaptive_channel_weights': weights,
        'q_learning_agent': agent,
        'voice_mode_manager': VoiceModeManager(),
        'zoom_mode_manager': ZoomModeManager(),
        'commands_presenter': FakeCommandsPresenter(),
        'command_catalog_provider': Mock(side_effect=get_command_catalog),
        'adaptive_runtime': SimpleNamespace(get_last_reward=Mock(return_value=0.38)),
    }


@pytest.fixture
def facade(dependencies):
    return ZeroUIApplicationFacade(**dependencies)


def test_system_status_active(facade):
    assert facade.get_system_status() == {
        'active': True, 'suspended': False, 'voice_mode': 'command',
        'zoom_enabled': False, 'commands_visible': False,
    }


def test_system_status_suspended(facade, dependencies):
    dependencies['system_mode_manager'].suspend()
    status = facade.get_system_status()
    assert status['active'] is False
    assert status['suspended'] is True


@pytest.mark.parametrize('mode', [VoiceMode.COMMAND, VoiceMode.DICTATION])
def test_voice_mode_uses_public_current_state(facade, dependencies, mode):
    if mode == VoiceMode.DICTATION:
        dependencies['voice_mode_manager'].activate_dictation()
    assert facade.get_system_status()['voice_mode'] == mode.value


@pytest.mark.parametrize('enabled', [False, True])
def test_zoom_state_uses_public_manager(facade, dependencies, enabled):
    dependencies['zoom_mode_manager'].set_enabled(enabled)
    assert facade.get_system_status()['zoom_enabled'] is enabled


@pytest.mark.parametrize('visible', [False, True])
def test_panel_visibility_uses_public_presenter(facade, dependencies, visible):
    if visible:
        dependencies['commands_presenter'].show_commands()
    assert facade.get_system_status()['commands_visible'] is visible


def test_activity_flags_come_from_one_state_read(dependencies):
    state = dependencies['system_mode_manager']
    state.is_suspended = Mock(side_effect=[False, True])
    state.is_active = Mock(return_value=False)
    status = ZeroUIApplicationFacade(**dependencies).get_system_status()
    assert status['active'] is True and status['suspended'] is False
    state.is_suspended.assert_called_once()
    state.is_active.assert_not_called()


def test_active_session_metrics_preserve_available_fields(facade, dependencies):
    snapshot = dependencies['session_manager'].get_snapshot.return_value
    assert facade.get_session_metrics() == {
        'session_active': True,
        'session_id': snapshot['session_id'],
        'started_at': snapshot['started_at'],
        **snapshot['metrics'],
    }
    dependencies['session_manager'].get_snapshot.assert_called_once()
    assert 'fatigue' not in facade.get_session_metrics()


def test_inactive_session_is_explicit_and_safe(facade, dependencies):
    dependencies['session_manager'].get_snapshot.return_value = None
    assert facade.get_session_metrics() == {'session_active': False}


def test_session_results_do_not_expose_mutable_source_counts(facade, dependencies):
    result = facade.get_session_metrics()
    result['source_counts']['head'] = -1
    result['total_events'] = -1
    result['extra'] = []
    assert facade.get_session_metrics()['source_counts']['head'] == 430
    assert facade.get_session_metrics()['total_events'] == 500
    assert 'extra' not in facade.get_session_metrics()


def test_adaptation_exposes_factors_weights_epsilon_and_existing_q_states(facade):
    assert facade.get_adaptation_state() == {
        'head_sensitivity_factor': 1.05,
        'limb_sensitivity_factor': 0.95,
        'weights': {'voice': 1.05, 'head': 1.0, 'limb': 1.0, 'gesture': 1.0},
        'epsilon': 0.0631,
        'q_states': 2,
        'last_reward': 0.38,
    }


def test_adaptation_queries_have_no_learning_side_effects(facade, dependencies, monkeypatch):
    agent = dependencies['q_learning_agent']
    parameters = dependencies['adaptive_parameters_manager']
    weights = dependencies['adaptive_channel_weights']
    before = (agent.get_q_table_snapshot(), agent.epsilon, parameters.snapshot(), weights.snapshot())
    forbidden = Mock(side_effect=AssertionError('A query must not run learning'))
    for method in ('choose_action', 'update', 'decay_exploration', 'get_q_value', 'get_state_values'):
        monkeypatch.setattr(agent, method, forbidden)
    monkeypatch.setattr(parameters, 'apply', forbidden)
    monkeypatch.setattr(weights, 'increase', forbidden)
    monkeypatch.setattr(weights, 'decrease', forbidden)
    for _ in range(3):
        facade.get_adaptation_state()
    assert (agent.get_q_table_snapshot(), agent.epsilon, parameters.snapshot(), weights.snapshot()) == before
    forbidden.assert_not_called()


def test_empty_q_table_stays_empty_when_queried(dependencies):
    agent = QLearningAgent(seed=1)
    dependencies['q_learning_agent'] = agent
    facade = ZeroUIApplicationFacade(**dependencies)
    assert facade.get_adaptation_state()['q_states'] == 0
    assert facade.get_adaptation_state()['q_states'] == 0
    assert agent.get_q_table_snapshot() == {}


def test_adaptation_read_is_available_while_suspended(facade, dependencies):
    before = facade.get_adaptation_state()
    dependencies['system_mode_manager'].suspend()
    assert facade.get_adaptation_state() == before


def test_last_reward_is_optional_and_uses_public_runtime_api(dependencies):
    facade = ZeroUIApplicationFacade(**dependencies)
    assert facade.get_adaptation_state()['last_reward'] == 0.38
    dependencies['adaptive_runtime'].get_last_reward.assert_called_once()
    dependencies['adaptive_runtime'] = None
    assert 'last_reward' not in ZeroUIApplicationFacade(**dependencies).get_adaptation_state()


def test_returned_weights_do_not_change_managers(facade):
    result = facade.get_adaptation_state()
    result['weights']['voice'] = -1
    result['head_sensitivity_factor'] = -1
    assert facade.get_adaptation_state()['weights']['voice'] == 1.05
    assert facade.get_adaptation_state()['head_sensitivity_factor'] == 1.05


def test_commands_reuse_catalog_and_match_existing_panel(facade, dependencies):
    catalog = facade.get_commands()
    dependencies['command_catalog_provider'].assert_called_once_with()
    assert catalog == get_command_catalog()
    assert set(catalog) == {'modes', 'execution', 'system', 'gestures'}
    panel = get_command_groups()
    assert panel[0][1] == catalog['modes'] + ['', 'CONTROLES ZEROUI', *catalog['system']]
    assert panel[1][1] == catalog['execution']
    assert panel[2][1] == catalog['gestures']
    assert 'enter' in catalog['execution']
    assert set(catalog['system']) == set(SYSTEM_CONTROL_COMMANDS)


def test_catalog_uses_live_command_sources(monkeypatch):
    monkeypatch.setattr('presentation.overlay.command_help.VOICE_COMMANDS', VOICE_COMMANDS + ['test phrase'])
    catalog = get_command_catalog()
    assert 'test phrase' in catalog['execution']
    assert 'test phrase' in get_command_groups()[1][1]


def test_commands_are_deep_copied_even_if_provider_caches_lists(dependencies):
    catalog = get_command_catalog()
    before = deepcopy(catalog)
    dependencies['command_catalog_provider'] = Mock(return_value=catalog)
    facade = ZeroUIApplicationFacade(**dependencies)
    result = facade.get_commands()
    for values in result.values():
        values.clear()
    assert catalog == before
    assert facade.get_commands() == before


@pytest.mark.parametrize('method,expected', [
    ('suspend', {'success': True, 'active': False, 'suspended': True}),
    ('activate', {'success': True, 'active': True, 'suspended': False}),
])
def test_system_controls_delegate_and_remain_idempotent(dependencies, monkeypatch, method, expected):
    state = dependencies['system_mode_manager']
    if method == 'activate':
        state.suspend()
    delegate = Mock(wraps=getattr(state, method))
    monkeypatch.setattr(state, method, delegate)
    facade = ZeroUIApplicationFacade(**dependencies)
    assert getattr(facade, method)() == expected
    assert getattr(facade, method)() == expected
    assert delegate.call_count == 2


def test_show_commands_delegates_without_duplicate_panels(facade, dependencies):
    assert facade.show_commands() == {'success': True, 'commands_visible': True}
    assert facade.show_commands() == {'success': True, 'commands_visible': True}
    presenter = dependencies['commands_presenter']
    assert presenter.show_calls == 2
    assert presenter.panels_created == 1


def test_hide_commands_delegates_idempotently(facade, dependencies):
    facade.show_commands()
    assert facade.hide_commands() == {'success': True, 'commands_visible': False}
    assert facade.hide_commands() == {'success': True, 'commands_visible': False}
    assert dependencies['commands_presenter'].hide_calls == 2


def test_control_does_not_claim_success_when_delegate_fails(dependencies):
    dependencies['commands_presenter'].show_commands = Mock(side_effect=RuntimeError('Unavailable'))
    with pytest.raises(RuntimeError, match='Unavailable'):
        ZeroUIApplicationFacade(**dependencies).show_commands()


def test_all_queries_return_json_serializable_values_without_printing(facade, capsys):
    for method in ('get_system_status', 'get_session_metrics', 'get_adaptation_state', 'get_commands'):
        result = getattr(facade, method)()
        assert json.loads(json.dumps(result)) == result
    facade.suspend()
    facade.activate()
    facade.show_commands()
    facade.hide_commands()
    assert capsys.readouterr().out == ''


def test_all_queries_leave_modes_panel_and_system_generation_unchanged(facade, dependencies):
    before = facade.get_system_status()
    generation = dependencies['system_mode_manager'].generation
    for method in ('get_system_status', 'get_session_metrics', 'get_adaptation_state', 'get_commands'):
        getattr(facade, method)()
    assert facade.get_system_status() == before
    assert dependencies['system_mode_manager'].generation == generation
    presenter = dependencies['commands_presenter']
    assert presenter.show_calls == presenter.hide_calls == 0
