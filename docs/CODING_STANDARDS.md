# AIStudio Coding Standards

**Version:** 2.0
**Status:** Active Standard
**Applies To:** Entire AIStudio Codebase

---

# 1. Purpose

This document defines the mandatory coding standards for AIStudio.

These standards ensure the codebase remains:

* Consistent
* Readable
* Maintainable
* Testable
* Enterprise quality

Every source file should appear as though it was written by the same developer.

This document defines **how code is written**.

System architecture is defined in **AISTUDIO_ARCHITECTURE.md**.

Agent implementation is defined in **AGENT_STANDARD.md**.

---

# 2. Guiding Principles

Every implementation must follow these principles.

1. Simplicity
2. Readability
3. Predictability
4. Single Responsibility
5. Explicit over Implicit
6. Maintainability over Cleverness
7. Consistency over Personal Preference

If two implementations solve the same problem, choose the one that is easiest to understand six months later.

---

# 3. Python Version

Minimum supported version:

```text
Python 3.13+
```

All code must be compatible with the project's supported Python version.

---

# 4. Formatting

The following tools are mandatory.

* Black
* isort
* Ruff

No manual formatting.

---

# 5. Line Length

Maximum line length:

```text
88 characters
```

Long function signatures may span multiple lines for readability.

---

# 6. Imports

Imports are grouped in the following order:

1. Standard Library
2. Third-party Libraries
3. Project Imports

Example:

```python
from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from shared.services import LLMService
```

Wildcard imports are prohibited.

---

# 7. Naming Conventions

## Classes

PascalCase

Example

```text
ProjectState
MotionDesignerAgent
ImageData
```

---

## Functions

snake_case

Example

```text
generate_script()
load_prompt()
register_asset()
```

---

## Variables

snake_case

Example

```text
project_state
scene_id
shot_number
```

---

## Constants

UPPER_CASE

Example

```text
DEFAULT_TIMEOUT
MAX_RETRIES
```

---

# 8. Type Hints

Every public function must define:

* Parameter types
* Return type

Example

```python
def run(
    self,
    state: ProjectState,
) -> ProjectState:
```

Return types must never be omitted.

---

# 9. Pydantic Models

All shared data structures are Pydantic models.

Rules:

* No business logic
* No API calls
* No filesystem access
* No networking

Models represent data only.

Mutable defaults must use:

```python
Field(default_factory=list)
```

or

```python
Field(default_factory=dict)
```

---

# 10. JSON Handling

JSON exists only at system boundaries.

Examples:

* LLM responses
* REST APIs
* Disk storage

Immediately convert JSON into Pydantic models.

Raw dictionaries must never propagate through the application.

---

# 11. File Headers

Every Python file begins with:

```python
from __future__ import annotations
```

Module docstrings should describe:

* Purpose
* Responsibility

Do not include copyright headers.

Git maintains history.

---

# 12. Comments

Comments explain **why**, not **what**.

Good

```python
# Retry because the provider occasionally truncates JSON responses.
```

Bad

```python
# Increment counter.
counter += 1
```

Avoid excessive commenting.

Readable code requires fewer comments.

---

# 13. Docstrings

Public classes require docstrings.

Public methods require docstrings where behaviour is not immediately obvious.

Avoid documenting trivial code.

---

# 14. Logging

Logging must use the project's logging framework.

Never use:

```python
print()
```

except inside tests or temporary debugging.

Log:

* Requests
* Responses
* Validation failures
* Exceptions

Never log:

* Chain of thought
* Sensitive information
* Entire prompt payloads unless debugging is explicitly enabled

---

# 15. Exceptions

Raise meaningful exceptions.

Bad

```python
raise Exception()
```

Good

```python
raise ValueError(
    "MotionData is required before MotionDesignerAgent runs."
)
```

Never swallow exceptions.

Never use empty except blocks.

---

# 16. Configuration

Configuration belongs in:

```text
config/
```

Never hardcode:

* URLs
* Ports
* API keys
* Directory paths
* Model names
* Provider names
* Timeouts

Read configuration through the project's configuration system.

---

# 17. Dependencies

Dependencies must follow the architecture.

Allowed:

```text
Agent
    ↓
Service
    ↓
Server
```

Forbidden:

```text
Service
    ↓
Agent
```

```text
Server
    ↓
Agent
```

```text
Agent
    ↓
Agent
```

---

# 18. One Responsibility Rule

Every file has one responsibility.

Good examples:

```text
llm_service.py
prompt_service.py
asset_service.py
motion.py
```

Bad examples:

```text
helpers.py
utils.py
misc.py
```

---

# 19. Testing

Every component requires corresponding tests.

Examples:

```text
tests/test_motion_designer.py
tests/test_prompt_service.py
tests/test_project_state.py
```

Testing must verify:

* Model validation
* Expected behaviour
* Error handling
* Service interaction
* State updates

No component is complete without tests.

---

# 20. Code Review Checklist

Before committing code, verify:

* Single responsibility
* Correct folder placement
* Uses shared services
* Uses Pydantic models
* Uses type hints
* Uses logging
* No duplicated logic
* No hardcoded configuration
* No wildcard imports
* Black formatted
* isort applied
* Ruff clean
* Tests passing
* Documentation updated where required

---

# 21. Performance Guidelines

Optimise only after correctness.

Prefer:

* Clear code
* Predictable behaviour
* Deterministic execution

Avoid premature optimisation.

Measure performance before refactoring for speed.

---

# 22. Security Guidelines

Never commit:

* API keys
* Passwords
* Tokens
* Secrets

Validate all external input.

Treat AI responses as untrusted until validated.

Use least privilege when interacting with external services.

---

# 23. Maintainability

Code should be understandable by a developer with no prior knowledge of the module.

Avoid unnecessary abstraction.

Avoid deeply nested logic.

Prefer composition over duplication.

Refactor duplicated code into shared services.

---

# 24. Definition of Done

Code is considered complete only when:

* It complies with AISTUDIO_ARCHITECTURE.md.
* It complies with AGENT_STANDARD.md where applicable.
* It follows every rule in this document.
* All tests pass.
* Documentation has been updated.
* The implementation is readable, deterministic, and production-ready.

---

# Golden Rule

Before committing any code, ask:

> **"Would this file look like it has always belonged in AIStudio?"**

If the answer is **No**, refactor it until the answer is **Yes**.
