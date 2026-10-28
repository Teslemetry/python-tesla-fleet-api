"""Private atomic files and a process lease (POSIX hosts only).

One service or login process per state directory. Approval uses a separate
short file lock so a human can approve while the service is running.
"""

import fcntl
import json
import os
import stat
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, cast


class Store:
    def __init__(self, root: Path):
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = root.lstat()
        if (
            not stat.S_ISDIR(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o077
        ):
            raise ValueError(
                "State directory must be owned by this user with mode 0700"
            )
        self.root = root

    @contextmanager
    def lock(self, name: str, *, blocking: bool = True) -> Iterator[None]:
        fd = os.open(self.root / name, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
            yield
        finally:
            os.close(fd)

    def read(self, name: str) -> dict[str, Any]:
        path = self.root / name
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        except FileNotFoundError:
            return {}
        with os.fdopen(fd) as stream:
            info = os.fstat(stream.fileno())
            if (
                info.st_uid != os.getuid()
                or info.st_mode & 0o077
                or not stat.S_ISREG(info.st_mode)
            ):
                raise ValueError("State file must be an owner-only regular file")
            value = json.load(stream)
        if not isinstance(value, dict):
            raise ValueError("Invalid state file")
        return cast(dict[str, Any], value)

    def write(self, name: str, value: dict[str, Any]) -> None:
        fd, temporary = tempfile.mkstemp(dir=self.root)
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump(value, stream, ensure_ascii=False, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.root / name)
            directory = os.open(self.root, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
