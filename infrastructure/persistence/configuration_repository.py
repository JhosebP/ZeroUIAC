import json
from pathlib import Path

from domain.models.calibration_profile import (
    CalibrationProfile
)


class ConfigurationRepository:

    def __init__(
        self,
        file_path="config/user_calibration.json"
    ):

        self.file_path = Path(file_path)

    def save(self, profile):

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                profile.to_dict(),
                file,
                indent=4,
                ensure_ascii=False
            )

    def load(self):

        if not self.file_path.exists():
            return CalibrationProfile()

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return CalibrationProfile.from_dict(
            data
        )