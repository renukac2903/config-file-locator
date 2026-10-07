"""Core search logic for locating configuration files by walking up the filesystem."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union


class ConfigNotFoundError(FileNotFoundError):
    """Raised when no matching config file exists between the start path and the filesystem root.

    Subclassing FileNotFoundError keeps the library interoperable with code that already
    catches the builtin when dealing with missing files.
    """


def _resolve_start(start: Optional[Union[str, os.PathLike]]) -> Path:
    """Normalize the caller-supplied start into an absolute directory Path.

    ``None`` means "the process's current working directory", which is the overwhelmingly
    common case for CLI tools and lets callers avoid threading cwd through every call.
    """
    if start is None:
        p = Path.cwd()
    else:
        p = Path(start)
    # We resolve to absolute form so the upward walk has a well-defined stopping point
    # (the filesystem root). Symlinks are resolved too: walking a symlinked subtree and
    # then continuing into the link's *target* ancestry would surprise callers who think
    # in terms of the path they typed. ``strict=False`` because the start directory need
    # not exist yet — e.g. searching from a path that will be created later — and the
    # caller gets a clearer ConfigNotFoundError than a RuntimeError from pathlib.
    return p.resolve(strict=False)


def find_config(
    filename: str,
    start: Optional[Union[str, os.PathLike]] = None,
) -> Optional[Path]:
    """Search upward from ``start`` for a file named ``filename``.

    Returns the Path of the first match found, or ``None`` if none exists between
    ``start`` and the filesystem root.

    Only regular files (or symlinks to regular files) are considered matches.
    A directory with the same name as ``filename`` is skipped, so a search for
    ``"config"`` will not stop at a directory named ``config``.
    """
    if not filename:
        # An empty filename would "match" the first directory checked via the
        # same-name-skip logic below, since no directory is named "". Returning
        # None here makes that impossibility explicit rather than relying on
        # incidental behavior.
        return None

    current = _resolve_start(start)
    seen: set[Path] = set()

    while True:
        # Guard against symlink loops that could otherwise make the upward walk
        # revisit the same resolved directory. On a normal filesystem this never
        # fires, but ``resolve()`` can produce cycles under exotic mounts.
        if current in seen:
            return None
        seen.add(current)

        candidate = current / filename
        # ``is_file()`` follows symlinks, so a symlink to a regular file counts.
        # A bare directory named ``filename`` returns False and is skipped.
        try:
            if candidate.is_file():
                return candidate
        except OSError:
            # is_file() can raise on broken symlinks in the directory or on paths
            # we lack permission to stat. Treat as "not a match" and keep walking
            # rather than aborting the whole search.
            pass

        parent = current.parent
        if parent == current:
            # Reached the filesystem root (``parent == self`` is pathlib's signal
            # for the root on both POSIX and Windows).
            return None
        current = parent


def locate_config(
    filename: str,
    start: Optional[Union[str, os.PathLike]] = None,
) -> Path:
    """Like :func:`find_config`, but raise :class:`ConfigNotFoundError` if no match exists.

    Use this when the absence of a config file is an error condition for the caller.
    """
    found = find_config(filename, start)
    if found is None:
        raise ConfigNotFoundError(
            f"No file named {filename!r} found between "
            f"{_resolve_start(start)} and the filesystem root"
        )
    return found
