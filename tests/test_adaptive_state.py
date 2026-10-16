from modules.adaptation.adaptive_state import (
    AdaptiveStateBuilder,
)


def create_metrics(
    duration=60.0,
    actions=0,
    errors=0,
    switches=0,
    voice=0,
    head=0,
    limb=0,
    gesture=0,
):

    return {
        "duration_seconds": duration,
        "action_events": actions,
        "error_events": errors,
        "channel_switches": switches,
        "source_counts": {
            "voice": voice,
            "head": head,
            "limb": limb,
            "gesture": gesture,
            "system": 0,
        },
    }


def test_empty_metrics_create_safe_state():

    builder = AdaptiveStateBuilder()

    state = builder.build({})

    assert state.voice_error_level == "low"
    assert state.activity_level == "low"
    assert state.switch_level == "low"
    assert state.dominant_source == "none"
    assert state.session_stage == "short"


def test_low_voice_error_level():

    builder = AdaptiveStateBuilder()

    state = builder.build(
        create_metrics(
            voice=10,
            errors=1,
        )
    )

    assert (
        state.voice_error_level
        == "low"
    )


def test_medium_voice_error_level():

    builder = AdaptiveStateBuilder()

    state = builder.build(
        create_metrics(
            voice=10,
            errors=2,
        )
    )

    assert (
        state.voice_error_level
        == "medium"
    )


def test_high_voice_error_level():

    builder = AdaptiveStateBuilder()

    state = builder.build(
        create_metrics(
            voice=10,
            errors=4,
        )
    )

    assert (
        state.voice_error_level
        == "high"
    )


def test_high_activity_level():

    builder = AdaptiveStateBuilder()

    state = builder.build(
        create_metrics(
            duration=60,
            actions=8,
        )
    )

    assert (
        state.activity_level
        == "high"
    )


def test_high_switch_level():

    builder = AdaptiveStateBuilder()

    state = builder.build(
        create_metrics(
            duration=60,
            switches=10,
        )
    )

    assert (
        state.switch_level
        == "high"
    )


def test_limb_can_be_dominant_source():

    builder = AdaptiveStateBuilder()

    state = builder.build(
        create_metrics(
            head=20,
            limb=80,
        )
    )

    assert (
        state.dominant_source
        == "limb"
    )


def test_balanced_sources_are_mixed():

    builder = AdaptiveStateBuilder()

    state = builder.build(
        create_metrics(
            head=55,
            limb=45,
        )
    )

    assert (
        state.dominant_source
        == "mixed"
    )


def test_session_stage_changes_with_duration():

    builder = AdaptiveStateBuilder()

    short_state = builder.build(
        create_metrics(
            duration=300,
        )
    )

    medium_state = builder.build(
        create_metrics(
            duration=900,
        )
    )

    long_state = builder.build(
        create_metrics(
            duration=2000,
        )
    )

    assert (
        short_state.session_stage
        == "short"
    )

    assert (
        medium_state.session_stage
        == "medium"
    )

    assert (
        long_state.session_stage
        == "long"
    )


def test_state_can_be_used_as_q_table_key():

    builder = AdaptiveStateBuilder()

    state = builder.build(
        create_metrics(
            voice=5,
            head=100,
            actions=3,
        )
    )

    key = state.as_key()

    assert isinstance(
        key,
        tuple,
    )

    assert len(key) == 5

def test_voice_state_uses_only_voice_errors():

    builder = AdaptiveStateBuilder()

    state = builder.build({
        "duration_seconds": 60.0,

        "action_events": 0,

        "error_events": 10,

        "voice_error_events": 0,

        "channel_switches": 0,

        "user_channel_switches": 0,

        "source_counts": {
            "voice": 10,
            "head": 0,
            "limb": 0,
            "gesture": 0,
        }
    })

    assert (
        state.voice_error_level
        == "low"
    )


def test_state_prefers_user_channel_switches():

    builder = AdaptiveStateBuilder()

    state = builder.build({
        "duration_seconds": 60.0,

        "action_events": 0,

        "error_events": 0,

        "voice_error_events": 0,

        "channel_switches": 20,

        "user_channel_switches": 0,

        "source_counts": {
            "voice": 0,
            "head": 10,
            "limb": 0,
            "gesture": 0,
        }
    })

    assert (
        state.switch_level
        == "low"
    )