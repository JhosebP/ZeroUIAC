import pytest

from modules.adaptation.session_persistence import (
    SessionPersistence
)


def create_summary(
    session_id="session-001"
):

    return {
        "session_id":
            session_id,

        "started_at":
            "2026-10-16T10:00:00+00:00",

        "ended_at":
            "2026-10-16T10:30:00+00:00",

        "metrics": {
            "total_events": 20
        },

        "fatigue": {
            "score": 0.25,
            "level": "low"
        }
    }


def test_save_creates_json_file(
    tmp_path
):

    persistence = (
        SessionPersistence(
            base_directory=tmp_path
        )
    )

    path = persistence.save(
        create_summary()
    )

    assert path.exists()

    assert (
        path.name
        == "session-001.json"
    )


def test_saved_session_has_schema_version(
    tmp_path
):

    persistence = (
        SessionPersistence(
            base_directory=tmp_path
        )
    )

    persistence.save(
        create_summary()
    )

    data = persistence.load(
        "session-001"
    )

    assert (
        data["schema_version"]
        == 1
    )

    assert (
        data["session_id"]
        == "session-001"
    )


def test_load_preserves_session_information(
    tmp_path
):

    persistence = (
        SessionPersistence(
            base_directory=tmp_path
        )
    )

    persistence.save(
        create_summary()
    )

    data = persistence.load(
        "session-001"
    )

    assert (
        data["metrics"]
        ["total_events"]
        == 20
    )

    assert (
        data["fatigue"]
        ["score"]
        == 0.25
    )


def test_missing_session_returns_none(
    tmp_path
):

    persistence = (
        SessionPersistence(
            base_directory=tmp_path
        )
    )

    assert (
        persistence.load(
            "does-not-exist"
        )
        is None
    )


def test_list_session_ids(
    tmp_path
):

    persistence = (
        SessionPersistence(
            base_directory=tmp_path
        )
    )

    persistence.save(
        create_summary(
            "session-b"
        )
    )

    persistence.save(
        create_summary(
            "session-a"
        )
    )

    assert (
        persistence.list_session_ids()
        == [
            "session-a",
            "session-b",
        ]
    )


def test_invalid_session_id_is_rejected(
    tmp_path
):

    persistence = (
        SessionPersistence(
            base_directory=tmp_path
        )
    )

    with pytest.raises(
        ValueError
    ):

        persistence.save(
            create_summary(
                "../outside"
            )
        )


def test_unicode_content_is_preserved(
    tmp_path
):

    persistence = (
        SessionPersistence(
            base_directory=tmp_path
        )
    )

    summary = create_summary()

    summary["description"] = (
        "Sesión de interacción"
    )

    persistence.save(
        summary
    )

    data = persistence.load(
        "session-001"
    )

    assert (
        data["description"]
        == "Sesión de interacción"
    )