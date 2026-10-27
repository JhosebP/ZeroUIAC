from dataclasses import replace

from main import print_adaptation_summary
from modules.adaptation.adaptive_actions import AdaptiveAction
from modules.adaptation.adaptive_channel_weights import ChannelWeightsSnapshot
from modules.adaptation.adaptive_parameters import AdaptiveParametersSnapshot
from modules.adaptation.adaptive_runtime_controller import AdaptationStepResult


def example_result():
    return AdaptationStepResult(
        action=AdaptiveAction.DECREASE_HEAD_SENSITIVITY,
        changed=True,
        reward=0.38,
        fatigue_score=0.42,
        state_key=('low', 'high', 'medium', 'head', 'short'),
        epsilon=0.0835,
        parameters_before=AdaptiveParametersSnapshot(1.05, 1.0),
        parameters_after=AdaptiveParametersSnapshot(1.0, 1.0),
        weights_before=ChannelWeightsSnapshot(1.0, 1.05, 1.0, 1.0),
        weights_after=ChannelWeightsSnapshot(1.0, 1.05, 1.0, 1.0),
        action_failure_rate=0.0,
        drag_failure_rate=0.0,
        correction_rate=0.04,
    )


def test_console_observer_formats_state_rates_and_actual_transitions(capsys):
    result = example_result()
    print_adaptation_summary(result)
    output = capsys.readouterr().out
    assert output.count('[ADAPTACIÓN]') == 1
    assert f'state_key: {result.state_key}' in output
    assert 'Canal dominante: head' in output
    assert 'Fallos acciones: 0.00' in output
    assert 'Fallos arrastre: 0.00' in output
    assert 'Correcciones cursor: 0.04' in output
    assert 'Fatiga: 0.42' in output
    assert 'Recompensa: 0.380' in output
    assert 'Acción elegida: DECREASE_HEAD_SENSITIVITY' in output
    assert 'Cambio aplicado: Sí' in output
    assert 'Cabeza: 1.05 -> 1.00' in output
    assert 'Cabeza: 1.05 -> 1.05' in output
    assert 'Extremidad: 1.00 -> 1.00' in output
    assert 'Epsilon: 0.0835' in output


def test_console_observer_marks_no_change_and_pending_first_reward(capsys):
    result = example_result()
    print_adaptation_summary(replace(
        result, action=AdaptiveAction.NO_CHANGE, changed=False, reward=None,
        parameters_after=result.parameters_before,
    ))
    output = capsys.readouterr().out
    assert 'Acción elegida: NO_CHANGE' in output
    assert 'Cambio aplicado: No' in output
    assert 'Recompensa: pendiente (primera adaptación)' in output
    assert 'Cabeza: 1.05 -> 1.05' in output


def test_console_observer_handles_unavailable_optional_snapshots(capsys):
    print_adaptation_summary(replace(
        example_result(), parameters_before=None, parameters_after=None,
        weights_before=None, weights_after=None,
    ))
    assert 'Cabeza: no disponible -> no disponible' in capsys.readouterr().out
