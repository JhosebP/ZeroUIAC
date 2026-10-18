import json
import re
import threading

from pathlib import Path


class SessionPersistence:
    """
    Persistencia local de sesiones
    de ZeroUI-AC en formato JSON.

    No depende de Internet ni de
    servicios externos.
    """

    SCHEMA_VERSION = 1

    SESSION_ID_PATTERN = re.compile(
        r"^[A-Za-z0-9_-]{1,128}$"
    )

    def __init__(
        self,
        base_directory="data/sessions"
    ):

        self._lock = (
            threading.RLock()
        )

        self.base_directory = Path(
            base_directory
        )

    def _validate_session_id(
        self,
        session_id
    ):

        if not isinstance(
            session_id,
            str
        ):

            raise ValueError(
                "Identificador de sesión inválido."
            )

        if not self.SESSION_ID_PATTERN.fullmatch(
            session_id
        ):

            raise ValueError(
                "Identificador de sesión inválido."
            )

        return session_id

    def _validate_summary(
        self,
        summary
    ):

        if not isinstance(
            summary,
            dict
        ):

            raise ValueError(
                "El resumen de sesión debe ser un diccionario."
            )

        session_id = (
            summary.get(
                "session_id"
            )
        )

        return self._validate_session_id(
            session_id
        )

    def _get_path(
        self,
        session_id
    ):

        session_id = (
            self._validate_session_id(
                session_id
            )
        )

        return (
            self.base_directory
            / f"{session_id}.json"
        )

    def save(
        self,
        summary
    ):
        """
        Guarda una sesión mediante
        escritura atómica.

        Primero escribe un archivo temporal
        y posteriormente reemplaza el archivo
        definitivo.
        """

        session_id = (
            self._validate_summary(
                summary
            )
        )

        with self._lock:

            self.base_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            final_path = (
                self._get_path(
                    session_id
                )
            )

            temporary_path = (
                self.base_directory
                / f".{session_id}.tmp"
            )

            payload = {
                **summary,

                "schema_version":
                    self.SCHEMA_VERSION,
            }

            try:

                with temporary_path.open(
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        payload,
                        file,
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True
                    )

                    file.flush()

                temporary_path.replace(
                    final_path
                )

            finally:

                if temporary_path.exists():

                    temporary_path.unlink()

            return final_path

    def load(
        self,
        session_id
    ):
        """
        Recupera una sesión almacenada.

        Devuelve None si todavía
        no existe.
        """

        with self._lock:

            path = self._get_path(
                session_id
            )

            if not path.exists():
                return None

            with path.open(
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(
                    file
                )

    def list_session_ids(
        self
    ):
        """
        Devuelve los identificadores
        disponibles localmente.
        """

        with self._lock:

            if (
                not self.base_directory
                .exists()
            ):

                return []

            return sorted(
                path.stem
                for path
                in self.base_directory.glob(
                    "*.json"
                )
                if path.is_file()
            )