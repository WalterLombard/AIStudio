# AIStudio Agent Standard

**Version:** 2.0
**Status:** Active Standard
**Applies To:** Every AI Agent within the AIStudio Production Pipeline

---

# 1. Purpose

This document defines the mandatory implementation standard for every AIStudio agent.

It establishes a single, consistent design pattern that every production department must follow.

Every agent must look, behave, and execute in the same manner regardless of its responsibility.

This document defines **how AI agents are implemented**.

Overall system architecture is defined in **AISTUDIO_ARCHITECTURE.md**.

General coding practices are defined in **CODING_STANDARDS.md**.

---

# 2. Design Philosophy

Every AIStudio agent represents a single department within a professional documentary production studio.

An agent exists to perform one clearly defined task.

An agent is an orchestrator.

It is **not** responsible for:

* Business logic
* Asset generation
* Configuration
* Pipeline orchestration
* Reusable utilities

Those responsibilities belong to shared services.

Agents translate approved upstream work into approved downstream work.

Nothing more.

---

# 3. Single Responsibility Principle

Each agent performs exactly one production task.

Examples:

* Executive Producer
* Research
* Outline
* Script Writer
* Storyboard
* Visual Planner
* Shot Planner
* Image Generator
* Motion Designer
* Narration Designer
* Voice Generator
* Music Generator
* SFX Generator
* Audio Mixer
* Video Compiler
* QA

No agent performs multiple production roles.

---

# 4. Standard Folder Structure

Every agent shall contain exactly the following files.

```text
agents/

    xxx/

        __init__.py

        agent.py

        prompt.md
```

The corresponding data models shall exist in:

```text
shared/models/xxx.py
```

Additional files should only be introduced when there is a clear architectural justification.

---

# 5. Standard Execution Lifecycle

Every AIStudio agent follows the exact same execution pattern.

```text
ProjectState
      │
      ▼
Validate Inputs
      │
      ▼
Load Prompt
      │
      ▼
Build JSON Payload
      │
      ▼
Single LLM Call
      │
      ▼
Validate JSON
      │
      ▼
Convert to Pydantic Model
      │
      ▼
Generate Assets (Optional)
      │
      ▼
Register Assets
      │
      ▼
Update ProjectState
      │
      ▼
Return ProjectState
```

No agent may deviate from this lifecycle without explicit architectural approval.

---

# 6. Standard Class Structure

Every agent follows the same implementation pattern.

```python
class ExampleAgent:

    def __init__(self):

        ...

    def _validate_state(...):

        ...

    def _build_payload(...):

        ...

    def _generate(...):

        ...

    def run(...):

        ...
```

Only the `run()` method is public.

All helper methods remain private.

---

# 7. Constructor Standard

Every constructor should initialise only the services required by the agent.

Example:

```python
self.llm = LLMService()

self.assets = AssetService()

self.system_prompt = PromptService.load_prompt(__file__)
```

Additional generation services may be added as required.

Example:

```python
ImageService

VoiceService

MusicService

SFXService

CompilerService
```

No processing occurs inside the constructor.

---

# 8. Input Validation

Every agent begins by validating its required upstream data.

Example:

```python
if state.storyboard is None:
    raise ValueError(...)
```

Validation occurs before any processing.

An agent must never assume upstream data exists.

Missing or invalid data immediately stops execution.

---

# 9. Payload Construction

Payload construction must be isolated from business logic.

Payloads shall be represented as Python dictionaries.

Example:

```python
payload = {

    ...

}
```

The payload shall then be serialised using:

```python
json.dumps(

    payload,

    indent=4,

    ensure_ascii=False,

)
```

This formatting is mandatory for consistency and debugging.

---

# 10. Prompt Standard

Every agent must contain a `prompt.md`.

Prompts shall follow the same structure.

1. Role
2. Purpose
3. Input Objects
4. Output Schema
5. Requirements
6. Rules

Prompts must be deterministic.

Prompts must return JSON only.

Prompts must never contain implementation details.

---

# 11. LLM Standard

Every LLM interaction must occur through:

```python
LLMService.generate_json()
```

Direct HTTP calls are prohibited.

Direct Ollama calls are prohibited.

Direct provider implementations are prohibited.

The LLM service is the only approved interface.

---

# 12. JSON Validation

LLM responses are considered untrusted.

Every response must immediately be converted into a Pydantic model.

Example:

```python
response = ExampleResponse(**result)
```

Raw dictionaries must never propagate through the application.

---

# 13. Asset Generation Standard

Where assets are generated, every agent follows the same lifecycle.

```text
LLM Plan
      │
      ▼
Generation Service
      │
      ▼
AssetRecord
      │
      ▼
AssetService.register()
      │
      ▼
Asset Library
      │
      ▼
ProjectState
```

Assets must never bypass the AssetService.

---

# 14. ProjectState Rules

An agent may update only:

* Its own output model.
* current_stage.
* status.

An agent must never modify another department's output.

ProjectState remains the single source of truth.

---

# 15. Deterministic AI Rules

AIStudio is deterministic.

Every downstream department translates approved upstream decisions.

An agent may:

* Translate
* Refine
* Validate
* Ground

An agent may never:

* Invent creative direction
* Rewrite upstream work
* Contradict approved decisions
* Introduce unrelated ideas

---

# 16. Error Handling

Agents follow a fail-fast philosophy.

Validation failures stop execution immediately.

Exceptions must clearly describe:

* The failing component.
* The reason for failure.
* The required upstream dependency.

Silent recovery is prohibited.

---

# 17. Logging

Agents should log:

* Start of execution
* Successful completion
* Validation failures
* Asset generation
* Exceptions

Sensitive information must never be logged.

Entire prompt payloads should only be logged when debug logging is enabled.

---

# 18. State Ownership

Every production department owns exactly one section of ProjectState.

Examples:

* Research owns `state.research`
* Script Writer owns `state.script`
* Motion Designer owns `state.motion`
* Music Generator owns `state.music`
* SFX Generator owns `state.sfx`

Ownership is exclusive.

---

# 19. Agent Independence

Agents never communicate directly.

Forbidden:

```text
Motion Designer
        ↓
Music Generator
```

Allowed:

```text
Motion Designer

        ↓

ProjectState

        ↓

Music Generator
```

ProjectState is the only communication mechanism between agents.

---

# 20. Testing Standard

Every completed agent must pass the following tests.

## Model Validation

* Pydantic models validate correctly.
* Invalid data is rejected.

---

## Prompt Loading

PromptService successfully loads the prompt.

---

## LLM Contract

Mocked JSON responses validate against response models.

---

## Agent Execution

The agent updates only:

* its own ProjectState section
* current_stage
* status

---

## Asset Registration

Generated assets register successfully through AssetService.

---

## Failure Handling

Invalid ProjectState produces meaningful exceptions.

---

## Deterministic Behaviour

Given identical inputs and deterministic model settings, the agent produces identical outputs.

---

# 21. Code Quality Requirements

Every agent shall:

* Follow the Coding Standards.
* Follow the Architecture Standard.
* Use strong typing.
* Use Pydantic.
* Use shared services.
* Use structured JSON.
* Remain deterministic.
* Remain modular.
* Be independently testable.

---

# 22. Definition of Done

An AIStudio agent is considered complete only when:

* All required files exist.
* Models validate successfully.
* Prompt loads successfully.
* Payload generation is deterministic.
* LLM responses validate successfully.
* Asset generation (where applicable) succeeds.
* Assets register successfully.
* ProjectState updates correctly.
* Unit tests pass.
* Integration tests pass.
* Documentation is complete.
* The implementation complies with all three governing standards.

---

# 23. Reference Implementation

The following agents should serve as reference implementations for all future development:

* Executive Producer
* Research Agent
* Outline Agent
* Script Writer
* Storyboard Agent
* Visual Planner
* Shot Planner
* **SFX Generator (post-refactor)**

All future agents should be modelled after the latest approved reference implementation to maintain consistency across the AIStudio codebase.

---

# Golden Rule

Before marking an agent as complete, ask:

> **"Does this agent behave exactly like every other AIStudio agent, differing only in its production responsibility?"**

If the answer is **No**, the implementation is not yet complete.
