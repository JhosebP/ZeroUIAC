from modules.adaptation.fatigue_estimator import (
    FatigueEstimator,
)


def create_low_snapshot():

    return {
        "duration_seconds": 300.0,

        "voice_error_rate": 0.0,

        "average_action_interval_seconds":
            1.0,

        "action_interval_samples": 5,

        "average_movement_magnitude":
            10.0,

        "movement_variability":
            1.0,

        "movement_samples": 10,

        "user_channel_switches": 0,

        "source_counts": {
            "voice": 10,
            "head": 10,
            "limb": 0,
            "gesture": 0,
        }
    }


def create_high_snapshot():

    return {
        "duration_seconds": 4000.0,

        "voice_error_rate": 0.50,

        "average_action_interval_seconds":
            10.0,

        "action_interval_samples": 10,

        "average_movement_magnitude":
            10.0,

        "movement_variability":
            12.0,

        "movement_samples": 20,

        "user_channel_switches": 20,

        "source_counts": {
            "voice": 20,
            "head": 20,
            "limb": 20,
            "gesture": 20,
        }
    }


def test_empty_snapshot_returns_low_fatigue():

    estimator = FatigueEstimator()

    result = estimator.estimate(
        {}
    )

    assert result.score == 0.0
    assert result.level == "low"


def test_none_snapshot_is_safe():

    estimator = FatigueEstimator()

    result = estimator.estimate(
        None
    )

    assert result.score == 0.0
    assert result.level == "low"


def test_low_operational_load_returns_low():

    estimator = FatigueEstimator()

    result = estimator.estimate(
        create_low_snapshot()
    )

    assert result.level == "low"

    assert (
        0.0
        <= result.score
        < estimator.LOW_MAX
    )


def test_high_operational_load_returns_high():

    estimator = FatigueEstimator()

    result = estimator.estimate(
        create_high_snapshot()
    )

    assert result.level == "high"

    assert (
        result.score
        >= estimator.MEDIUM_MAX
    )


def test_score_is_always_bounded():

    estimator = FatigueEstimator()

    snapshot = (
        create_high_snapshot()
    )

    snapshot[
        "voice_error_rate"
    ] = 100.0

    snapshot[
        "user_channel_switches"
    ] = 100000

    result = estimator.estimate(
        snapshot
    )

    assert (
        0.0
        <= result.score
        <= 1.0
    )


def test_long_session_alone_is_not_high_fatigue():

    estimator = FatigueEstimator()

    result = estimator.estimate({
        "duration_seconds": 7200.0
    })

    assert result.score == 0.25

    assert result.level == "low"


def test_voice_component_requires_voice_events():

    estimator = FatigueEstimator()

    result = estimator.estimate({
        "duration_seconds": 60.0,

        "voice_error_rate": 1.0,

        "source_counts": {
            "voice": 0
        }
    })

    assert (
        result.voice_error_component
        == 0.0
    )


def test_movement_component_uses_relative_variability():

    estimator = FatigueEstimator()

    result = estimator.estimate({
        "duration_seconds": 60.0,

        "average_movement_magnitude":
            10.0,

        "movement_variability":
            10.0,

        "movement_samples": 10,
    })

    assert (
        result.movement_component
        == 1.0
    )


def test_single_movement_sample_does_not_create_fatigue():

    estimator = FatigueEstimator()

    result = estimator.estimate({
        "average_movement_magnitude":
            10.0,

        "movement_variability":
            10.0,

        "movement_samples": 1,
    })

    assert (
        result.movement_component
        == 0.0
    )


def test_nested_session_snapshot_is_supported():

    estimator = FatigueEstimator()

    result = estimator.estimate({
        "session_id": "test",

        "metrics":
            create_high_snapshot()
    })

    assert result.level == "high"


def test_invalid_numeric_values_are_safe():

    estimator = FatigueEstimator()

    result = estimator.estimate({
        "duration_seconds":
            "invalido",

        "voice_error_rate":
            None,

        "average_action_interval_seconds":
            "error",

        "movement_variability":
            float("nan"),

        "average_movement_magnitude":
            float("inf"),
    })

    assert result.score == 0.0
    assert result.level == "low"