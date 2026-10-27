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

def test_limb_factor_defaults_to_one_without_manager():

    service = (
        create_service_without_camera()
    )

    service.adaptive_parameters_manager = (
        None
    )

    assert (
        service
        ._get_limb_sensitivity_factor()
        == 1.0
    )


def test_limb_factor_is_read_from_manager():

    service = (
        create_service_without_camera()
    )

    service.adaptive_parameters_manager \
        .snapshot \
        .return_value = (
            SimpleNamespace(
                head_sensitivity_factor=1.0,
                limb_sensitivity_factor=1.20
            )
        )

    assert (
        service
        ._get_limb_sensitivity_factor()
        == 1.20
    )


def test_limb_adaptation_failure_falls_back_to_one():

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
        ._get_limb_sensitivity_factor()
        == 1.0
    )

def test_process_limb_passes_adaptive_factor_to_mapper():

    service = (
        MultimodalVisionService
        .__new__(
            MultimodalVisionService
        )
    )

    service.event_bus = MagicMock()

    service.hand_tracker = MagicMock()

    service.gesture_detector = (
        MagicMock()
    )

    service.limb_mapper = MagicMock()

    service.mouse = MagicMock()

    service.profile = (
        SimpleNamespace(
            selected_limb="right"
        )
    )

    service.adaptive_parameters_manager = (
        MagicMock()
    )

    service.adaptive_parameters_manager \
        .snapshot \
        .return_value = (
            SimpleNamespace(
                limb_sensitivity_factor=1.20
            )
        )

    service.hand_stable_frames = 0
    service.required_hand_frames = 1

    service.last_hand_seen_time = 0.0

    service.hand_smoothing = 1.0

    service.smoothed_hand_x = None
    service.smoothed_hand_y = None

    service.last_limb_position = None

    service.limb_min_step = 0

    landmarks = object()

    service.hand_tracker \
        .get_selected_hand \
        .return_value = {
            "landmarks": landmarks,
            "score": 1.0
        }

    service.gesture_detector \
        .detect \
        .return_value = None

    service.hand_tracker \
        .get_palm_center_position \
        .return_value = {
            "x": 0.8,
            "y": 0.5
        }

    service.mouse \
        .get_virtual_screen_bounds \
        .return_value = (
            0,
            0,
            1000,
            800
        )

    service.limb_mapper \
        .calculate \
        .return_value = (
            800,
            400
        )

    frame = MagicMock()

    service._process_limb(
        frame
    )

    service.limb_mapper \
        .calculate \
        .assert_called_once_with(
            0.8,
            0.5,
            1000,
            800,
            sensitivity_factor=1.20
        )

def test_missing_landmarks_resets_head_mapper_without_publishing():
    service = create_service_without_camera()
    service.face_tracker.get_landmarks.return_value = None

    service._process_head(MagicMock())

    service.head_mapper.reset.assert_called_once_with()
    service.head_mapper.calculate.assert_not_called()
    service.head_pose.estimate.assert_not_called()
    service.event_bus.publish.assert_not_called()


def test_missing_pose_resets_head_mapper_without_publishing():
    service = create_service_without_camera()
    service.face_tracker.get_landmarks.return_value = object()
    service.head_pose.estimate.return_value = None
    frame = SimpleNamespace(shape=(720, 1280, 3))

    service._process_head(frame)

    service.head_mapper.reset.assert_called_once_with()
    service.head_mapper.calculate.assert_not_called()
    service.event_bus.publish.assert_not_called()


def test_recovered_face_starts_head_smoothing_from_zero():
    from modules.vision.head_cursor_mapper import HeadCursorMapper

    for missing_landmarks in (True, False):
        service = create_service_without_camera()
        service.head_mapper = HeadCursorMapper()
        for _ in range(5):
            service.head_mapper.calculate(12.0, 12.0, 0.0, 0.0)
        service.face_tracker.get_landmarks.return_value = (
            None if missing_landmarks else object()
        )
        service.head_pose.estimate.return_value = None
        frame = SimpleNamespace(shape=(720, 1280, 3))

        service._process_head(frame)
        assert service.head_mapper.previous_dx == 0.0
        assert service.head_mapper.previous_dy == 0.0
        service.event_bus.publish.assert_not_called()

        service.face_tracker.get_landmarks.return_value = object()
        service.head_pose.estimate.return_value = {'yaw': -12.0, 'pitch': -12.0}
        service._process_head(frame)

        event = service.event_bus.publish.call_args.args[0]
        assert event.payload == {'mode': 'relative', 'dx': 7, 'dy': -7}
