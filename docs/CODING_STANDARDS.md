# AIStudio Coding Standards

Version: 1.0

---

# Purpose

This document defines the coding standards for the AIStudio project.

These standards are mandatory.

Every Python file, prompt, service, model and agent must follow these conventions.

The goal is to ensure the codebase remains:

- Consistent
- Readable
- Maintainable
- Testable
- Production quality

Every file should appear as though it was written by the same developer.

---

# Philosophy

The project follows five principles.

1. Simplicity
2. Readability
3. Single Responsibility
4. Predictability
5. Explicit over Implicit

If there are two possible implementations, choose the one that is easier to understand six months from now.

---

# Project Architecture

AIStudio is divided into clearly separated layers.

```
GUI

↓

Orchestrator

↓

Agents

↓

Shared Services

↓

Servers

↓

AI Models
```

No layer may bypass another layer.

---

# Directory Responsibilities

## agents/

Contains AI agents.

Each agent owns exactly one responsibility.

Examples

- Executive Producer
- Research Agent
- Outline Agent
- Script Writer

Agents never communicate directly with each other.

The orchestrator coordinates them.

---

## shared/services/

Contains reusable business logic.

Examples

- LLMService
- PromptService
- MemoryService
- CacheService
- AssetService

Services contain reusable code.

Agents consume services.

---

## shared/models/

Contains only Pydantic models.

No business logic.

No API calls.

No filesystem operations.

Only data.

---

## orchestrator/

Coordinates workflow.

Never contains AI prompts.

Never contains business logic.

---

## servers/

Interfaces with external engines.

Examples

Video Server

Audio Server

Compiler Server

---

## config/

Configuration only.

No code.

---

## prompts/

Prompt templates only.

---

## tests/

Unit tests.

One test file per component.

---

# Imports

Always group imports.

Example

```python
from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from shared.services.llm_service import LLMService
```

Import order

1 Standard Library

2 Third-party Libraries

3 Project Imports

---

# Line Length

Maximum

88 characters

Use Black formatting.

---

# Blank Lines

Use one blank line between logical blocks.

Use two blank lines between classes.

Example

```python
class FirstClass:
    ...


class SecondClass:
    ...
```

---

# Comments

Only write comments when they explain WHY.

Never explain WHAT obvious code is doing.

Good

```python
# Retry because Ollama occasionally truncates long JSON.
```

Bad

```python
# Increment counter.
counter += 1
```

---

# File Headers

Every file starts with

```python
from __future__ import annotations
```

No copyright headers.

No author headers.

Git tracks history.

---

# Class Naming

PascalCase

Example

```python
ExecutiveProducer

ResearchAgent

OutlineData

ProjectManager
```

---

# Function Naming

snake_case

Example

```python
generate_outline()

save_project()

load_prompt()
```

---

# Variable Naming

snake_case

Good

```python
project_state

scene_count

production_brief
```

Bad

```python
projectState

SceneCount

pb
```

---

# Constants

UPPER_CASE

Example

```python
DEFAULT_TIMEOUT = 60
```

---

# Type Hints

Every function must include type hints.

Example

```python
def run(
    self,
    state: ProjectState,
) -> ProjectState:
```

Never omit return types.

---

# Pydantic Models

Every shared data structure is a Pydantic model.

Never use raw dictionaries internally.

Bad

```python
project["title"]
```

Good

```python
project.title
```

---

# JSON

JSON exists only at system boundaries.

Example

LLM

Disk

REST API

Immediately convert JSON into Pydantic models.

Never pass dictionaries through the application.

---

# Services

Services should never know about agents.

Agents consume services.

Never the reverse.

---

# Agents

Every agent contains

```
agent.py

prompt.md

__init__.py
```

Nothing else.

---

# Prompt Files

Prompt files are Markdown.

Never embed prompts inside Python.

Good

```
prompt.md
```

Bad

```python
prompt = """
...
"""
```

---

# Logging

Every service logs.

Every agent logs.

Never use print() except inside tests.

Example

```python
logger.info(...)

logger.warning(...)

logger.error(...)
```

---

# Exceptions

Raise meaningful exceptions.

Bad

```python
raise Exception()
```

Good

```python
raise ValueError(
    "ProductionBrief is missing."
)
```

---

# Testing

Every component has a matching test.

Example

```
agents/researcher/

tests/test_research_agent.py
```

Never merge code without a passing test.

---

# Formatting

Black

isort

ruff

No manual formatting.

---

# Docstrings

Use docstrings only for public classes or complex methods.

Avoid documenting obvious code.

---

# One Responsibility Rule

Each file should have one responsibility.

Examples

Good

```
llm_service.py

prompt_service.py

memory_service.py
```

Bad

```
utils.py

helpers.py

misc.py
```

---

# Dependency Rules

Allowed

Agent

↓

Service

↓

Server

Not Allowed

Service

↓

Agent

---

# Configuration

Never hardcode

URLs

Ports

Model names

Directories

Read them from

```
config.yaml
```

---

# AI Responses

Always validate AI output.

Never trust raw LLM responses.

Convert immediately into

Pydantic models.

---

# Prompt Engineering

Prompt files must

Define the role

Define the task

Define the input

Define the output

Specify JSON schema

Specify constraints

Specify failure conditions

Never leave output ambiguous.

---

# Future Components

Every future component must fit this architecture.

Examples

Storyboard Agent

Visual Director

Image Critic

Motion Director

Audio Director

QA Agent

Publisher

No component may violate the dependency rules.

---

# Code Review Checklist

Before committing code verify

✓ One responsibility

✓ Correct folder

✓ Uses services

✓ Uses Pydantic

✓ Uses logging

✓ Uses type hints

✓ No duplicated logic

✓ No hardcoded paths

✓ No hardcoded models

✓ Tested

✓ Black formatted

✓ Imports sorted

✓ Prompt stored in prompt.md

---

# Golden Rule

When writing new code ask:

"Would this look like it has always been part of AIStudio?"

If the answer is no, rewrite it.