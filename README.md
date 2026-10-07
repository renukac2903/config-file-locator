# Config File Locator

Searches upward from a starting path for a named config file and returns the first match.

```python
from config_file_locator import find_config, locate_config, ConfigNotFoundError

# find_config returns a Path or None
path = find_config("pyproject.toml", start=".")

# locate_config raises if nothing is found
try:
    path = locate_config("pyproject.toml")
except ConfigNotFoundError:
    path = None
```

## Why

Tools that load configuration usually want to find the closest matching file to the
current working directory — the nearest `.eslintrc`, the enclosing `pyproject.toml`,
and so on. Writing that walk inline means re-implementing "go up until root" every
time, and getting the stopping condition wrong is easy.

This library does exactly that walk and nothing else. It does not parse the file,
merge multiple matches, or understand any config format. If you need layered
configuration (base file plus overrides), call `find_config` once and parse the
result yourself; that is a separate problem.

## Edge cases

- A directory with the same name as the target file is skipped — only regular
  files (or symlinks to regular files) count as matches.
- An empty filename returns `None` rather than raising.
- The start path is resolved (symlinks followed) before walking, so the search
  follows the physical ancestry of the resolved path, not the lexical one.
