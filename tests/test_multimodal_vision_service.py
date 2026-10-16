from collections import deque
from types import SimpleNamespace
from unittest.mock import MagicMock

from application.interaction.multimodal_vision_service import (
    MultimodalVisionService,
)


def create_service_without_camera(
    factor=1.0
):

    service = (
        MultimodalVisionService
        .__new__(
            MultimodalVisionService
        )
    )

    service.event_bus = MagicMock()

    service.face_tracker = MagicMock()
    service.head_pose = MagicMock()

    service.head_mapper = MagicMock()

    service.head_zoom_detector = (
        MagicMock()
    )

    service.head_zoom_detector \
        .is_active = False

    service.zoom_mode_manager = (
        MagicMock()
    )

    service.zoom_mode_manager \
        .is_enabled \
        .return_value = False

    service.profile = (
        SimpleNamespace(
            is_calibrated=True,
            neutral_yaw=0.0,
            neutral_pitch=0.0,
        )
    )

    service.pose_history = deque(
        maxlen=30
    )

    service.range_calibration = False

    service._limb_has_control = (
        MagicMock(
            return_value=False
        )
    )

    manager = MagicMock()

    manager.snapshot.return_value = (
        SimpleNamespace(
            head_sensitivity_factor=(
                factor
            )
        )
    )

    service.adaptive_parameters_manager = (
        manager
    )

    return service


def test_head_factor_defaults_to_one_without_manager():

    service = (
        create_service_without_camera()
    )

    service.adaptive_parameters_manager = (
        None
    )

    assert (
        service
        ._get_head_sensitivity_factor()
        == 1.0
    )


def test_head_factor_is_read_from_manager():

    service = (
        create_service_without_camera(
            factor=1.05
        )
    )

    assert (
        service
        ._get_head_sensitivity_factor()
        == 1.05
    )


def test_adaptation_failure_falls_back_to_one():

    service = (
        create_service_without_camera()
    )

    service.adaptive_parameters_manager \
        .snapshot \
        .side_effect = RuntimeError(
            "fallo de prueba"
        )

    assert (
        service
        ._get_head_sensitivity_factor()
        == 1.0
    )


def test_process_head_passes_adaptive_factor_to_mapper():

    service = (
        create_service_without_camera(
            factor=1.05
        )
    )

    frame = MagicMock()

    frame.shape = (
        720,
        1280,
        3,
    )

    landmarks = object()

    service.face_tracker \
        .get_landmarks \
        .return_value = landmarks

    service.head_pose \
        .estimate \
        .return_value = {
            "yaw": 12.0,
            "pitch": 4.0,
        }

    service.head_mapper \
        .calculate \
        .return_value = (
            5,
            2,
        )

    service._process_head(
        frame
    )

    service.head_mapper \
        .calculate \
        .assert_called_once_with(
            12.0,
            4.0,
            0.0,
            0.0,
            sensitivity_factor=1.05,
        )