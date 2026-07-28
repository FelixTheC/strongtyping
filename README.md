[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/release/python-3140/)
[![PyPI version](https://badge.fury.io/py/strongtyping.svg)](https://badge.fury.io/py/strongtyping)
![Python application](https://github.com/FelixTheC/strongtyping/actions/workflows/python-app.yml/badge.svg)
![image](https://codecov.io/gh/FelixTheC/strongtyping/graph/badge.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Documentation Status](https://readthedocs.org/projects/strongtyping/badge/?version=latest)](https://strongtyping.readthedocs.io/en/latest/?badge=latest)
[![](https://img.shields.io/pypi/dm/strongtyping.svg)](https://pypi.org/project/strongtyping/)
[![AI Agents](https://img.shields.io/badge/AI_Agents-SKILL.md-blue?logo=robotframework&logoColor=white)](SKILL.md)

# Strong Typing

<p>Decorator which <b>checks at Runtime</b> whether the function is called with the correct type of parameters.<br> 
And <b><em>raises</em> TypeMisMatch</b> if the used parameters in a function call where invalid.</p>

# This is the release for Python-3.14 and above

- If you need a different version please checkout the release Tags 2.\*.*

## Performance boost with mypyc

- Since __3.13.6__ `mypyc` is used to compile the core logic code.
- This results in a significant performance boost from around __5x faster__, especially for large containers.

## Async functions

Use the dedicated `a_match_typing` decorator for `async def` functions. It preserves the coroutine interface while
validating annotated arguments before the function runs.

```python
from strongtyping.astrong_typing import a_match_typing
import asyncio


@a_match_typing
async def add(left: int, right: int) -> int:
    return left + right


async def main() -> None:
    result = await add(1, 2)  # 3
    await add(1, "2")  # raises TypeMismatch


asyncio.run(main())
```

See the [async type checking documentation](https://strongtyping.readthedocs.io/en/latest/async_match_typing/)
for configuration options and further examples.

### 🤖 AI Agent Ready

This library includes [Agent Skills](https://agentskills.io/) for AI coding assistants (like Claude Code, Cursor, and
GitHub Copilot). These skills provide the AI with specialized knowledge on how to apply runtime type checking, handle
`TypeMismatch` exceptions, and follow best practices when using `strongtyping` in your codebase.

You can validate the skills by running:

```bash
pytest tests/test_skills.py
```

## [Docs are available on 'readthedocs'](https://strongtyping.readthedocs.io/en/latest/#the-solution)
