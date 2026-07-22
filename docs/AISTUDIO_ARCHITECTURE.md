# AIStudio Architecture Standard

**Version:** 2.0
**Status:** Active Standard
**Applies To:** Entire AIStudio Codebase

---

# 1. Purpose

This document defines the architecture of AIStudio.

It is the governing standard for every component in the project.

All agents, services, models, orchestration logic and future components must conform to this architecture.

If any implementation conflicts with this document, this document takes precedence.

---

# 2. Vision

AIStudio is a fully local, deterministic, AI-powered documentary production platform.

Its objectives are:

* Enterprise-quality software architecture.
* Modular and maintainable code.
* Deterministic AI behaviour.
* Complete local execution.
* Production-quality documentary generation.
* Extensible architecture for future production departments.
* Clear separation of responsibilities.

AIStudio is not a chatbot.

AIStudio is not a generic AI framework.

AIStudio is a virtual film production studio.

---

# 3. Core Design Philosophy

AIStudio models a professional documentary production studio.

Each AI agent represents one specialist department.

Examples include:

* Executive Producer
* Research Department
* Script Writer
* Storyboard Artist
* Cinematographer
* Motion Designer
* Narration Director
* Sound Designer
* Music Composer
* Audio Engineer
* Video Editor
* Quality Assurance

Each department performs one specialised task.

No department performs multiple unrelated responsibilities.

Creative authority flows only from upstream departments to downstream departments.

---

# 4. Architectural Principles

Every component must follow these principles.

## 4.1 Single Responsibility

Each agent performs exactly one responsibility.

No agent combines multiple production roles.

---

## 4.2 Deterministic Execution

Agents translate approved decisions.

Agents do not redesign upstream creative work.

---

## 4.3 JSON First

All LLM interactions return JSON.

Natural language responses are never processed.

---

## 4.4 Strong Typing

All data is represented by Pydantic models.

Raw dictionaries exist only at system boundaries.

---

## 4.5 ProjectState

ProjectState is the single source of truth.

Every agent receives ProjectState.

Every agent returns ProjectState.

---

## 4.6 Thin Agents

Agents orchestrate work.

Business logic belongs inside services.

Creative reasoning belongs inside prompts.

---

## 4.7 Shared Services

Reusable functionality belongs in shared/services.

Services never know about individual agents.

---

## 4.8 Fail Fast

Errors stop the pipeline immediately.

Invalid data is never silently ignored.

---

## 4.9 Local First

All processing should execute locally whenever possible.

External services are optional integrations.

---

## 4.10 Enterprise Maintainability

The codebase must remain understandable years after development.

Readability is always preferred over clever implementations.

---

# 5. Repository Architecture

```
agents/
config/
docs/
output/
servers/
shared/
tests/
```

## agents/

Contains every AI production department.

Each folder contains:

```
agent.py
prompt.md
__init__.py
```

---

## shared/

Contains reusable code.

```
models/
services/
utilities/
```

---

## config/

Configuration only.

No executable logic.

---

## docs/

Project standards.

Architecture.

Design decisions.

---

## servers/

Interfaces with external generation engines.

Examples:

* Image Server
* Audio Server
* Compiler Server

---

## output/

Generated production assets.

Images.

Video.

Audio.

Temporary files.

---

## tests/

Unit tests.

Integration tests.

Pipeline validation.

---

# 6. Production Pipeline

The production pipeline executes sequentially.

```
Executive Producer
        ↓
Research
        ↓
Outline
        ↓
Script Writer
        ↓
Storyboard
        ↓
Visual Planner
        ↓
Shot Planner
        ↓
Image Generator
        ↓
Motion Designer
        ↓
Narration Designer
        ↓
Voice Generator
        ↓
Music Generator
        ↓
SFX Generator
        ↓
Audio Mixer
        ↓
Video Compiler
        ↓
Quality Assurance
```

Each stage consumes approved work from the previous stage.

No stage redesigns previous work.

---

# 7. ProjectState Lifecycle

ProjectState is the central production record.

Every agent:

Receives

```
ProjectState
```

Returns

```
ProjectState
```

An agent may only modify:

* Its own output model.
* current_stage.
* status.

Agents must never modify another department's output.

---

# 8. Data Flow

Creative planning transitions from scenes to shots.

```
Production Brief
        ↓
Research
        ↓
Outline
        ↓
Script
        ↓
Storyboard Scene
        ↓
Storyboard Shot
        ↓
Shot Specification
        ↓
Image
        ↓
Motion
        ↓
Narration
        ↓
Voice
        ↓
Music
        ↓
SFX
        ↓
Audio Mix
        ↓
Video
```

From the Shot Planner onward, all downstream processing operates on individual shots.

---

# 9. Shot Continuity

Every downstream production stage preserves continuity using:

* scene_id
* shot_number
* image_asset_id
* start_time
* end_time

These identifiers remain unchanged throughout the remainder of the pipeline.

---

# 10. Asset Lifecycle

Every generated asset follows the same lifecycle.

```
LLM Planning
        ↓
Generation Service
        ↓
AssetRecord
        ↓
AssetService Registration
        ↓
Asset Library
        ↓
ProjectState
```

Every generated asset must be traceable.

---

# 11. Agent Responsibilities

Agents are responsible for:

* Validating upstream state.
* Loading prompts.
* Building JSON payloads.
* Calling the LLM.
* Validating responses.
* Registering generated assets.
* Updating ProjectState.

Agents are not responsible for:

* Modifying upstream creative decisions.
* Calling other agents.
* Direct server communication outside approved services.
* Pipeline orchestration.

---

# 12. Services Layer

Shared services contain reusable functionality.

Examples include:

* LLMService
* PromptService
* AssetService
* ImageService
* MotionService
* VoiceService
* MusicService
* SFXService

Services never contain project orchestration.

Services never know about agents.

---

# 13. Dependency Rules

Allowed

```
Agent
    ↓
Service
    ↓
Server
```

Not Allowed

```
Server
    ↓
Agent
```

```
Service
    ↓
Agent
```

```
Agent
    ↓
Agent
```

All coordination occurs through the orchestrator and ProjectState.

---

# 14. Deterministic AI Rules

Creative ownership exists only upstream.

Downstream agents execute approved decisions.

Agents may:

* Translate.
* Refine.
* Ground.
* Validate.

Agents may never:

* Invent new creative direction.
* Rewrite approved work.
* Contradict upstream decisions.
* Introduce unrelated content.

Identical inputs should produce identical outputs whenever deterministic generation is enabled.

---

# 15. Prompt Philosophy

Prompts define creative reasoning.

Python orchestrates execution.

Prompts must produce structured JSON only.

Prompt engineering must remain deterministic and production-oriented.

---

# 16. Asset Management

Every generated asset must include:

* Asset ID.
* Provider.
* Source stage.
* Scene reference.
* Shot reference.
* Duration.
* Metadata.

Assets must remain reproducible and traceable throughout the pipeline.

---

# 17. Pipeline Execution

The orchestrator executes agents sequentially.

Execution stops immediately when validation fails.

Successful completion updates:

* ProjectState
* current_stage
* status

The next agent receives the updated ProjectState.

---

# 18. Error Philosophy

AIStudio follows a fail-fast philosophy.

Validation failures immediately stop execution.

Exceptions must clearly explain:

* What failed.
* Where it failed.
* Why it failed.
* How it can be corrected.

Silent recovery is prohibited.

---

# 19. Configuration Management

Configuration belongs exclusively within:

```
config/
```

The following values must never be hardcoded:

* Model names.
* Provider names.
* Ports.
* URLs.
* File locations.
* Output directories.
* Timeouts.

---

# 20. Testing Philosophy

Every component must be independently testable.

Testing includes:

* Unit tests.
* Service tests.
* Model validation.
* Prompt loading.
* Agent execution.
* Pipeline integration.

All agents must pass testing before integration into the production pipeline.

---

# 21. Future Expansion

Future production departments may be added provided they:

* Follow the Agent Standard.
* Maintain deterministic execution.
* Respect ProjectState ownership.
* Preserve dependency rules.
* Integrate into the production pipeline without breaking existing stages.

---

# 22. Definition of Done

A component is considered complete only when all of the following are true:

* Architecture complies with this document.
* Coding complies with CODING_STANDARDS.md.
* Agent implementation complies with AGENT_STANDARD.md.
* Models validate successfully.
* Prompts produce valid JSON.
* Services operate correctly.
* Assets register successfully.
* Unit tests pass.
* Integration tests pass.
* Pipeline execution succeeds.
* Documentation is complete.

Only components meeting every requirement may be considered production-ready.
