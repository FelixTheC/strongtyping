from pathlib import Path
from types import ModuleType
from typing import Any

import tomllib


class Config:
    pyproject_toml_path: Path | None
    pyproject_toml: dict[str, Any] | None

    __slots__ = ("pyproject_toml_path", "pyproject_toml")

    def __init__(self) -> None:
        self.pyproject_toml_path = None
        self.pyproject_toml = None

        for path in Path.cwd().parents:
            pyproject_toml_path = path / "pyproject.toml"
            if pyproject_toml_path.exists():
                self.pyproject_toml_path = pyproject_toml_path
                break

    def load(self) -> None:
        if self.pyproject_toml_path is None:
            return
        with self.pyproject_toml_path.open("rb") as fp:
            self.pyproject_toml = tomllib.load(fp).get("tool", {}).get("strongtyping")

    @property
    def severity(self) -> Any | None:  # noqa:  `Any` to avoid circular import errors
        from strongtyping.utils import SEVERITY_CONFIG

        if not self.pyproject_toml:
            return None

        return SEVERITY_CONFIG.get(self.pyproject_toml.get("severity", "enable"))

    @property
    def custom_exception(self) -> Any:
        if not self.pyproject_toml:
            return None

        custom_exception_module: str | None = self.pyproject_toml.get("custom_exception")
        if custom_exception_module is None:
            return None

        import importlib

        *exception_module_path, exception_module_class = custom_exception_module.split(".")

        exception_module: ModuleType = importlib.import_module(".".join(exception_module_path))
        return getattr(exception_module, exception_module_class)

    @property
    def project_root(self) -> Path | None:
        if self.pyproject_toml_path:
            return self.pyproject_toml_path.parent
        return None
