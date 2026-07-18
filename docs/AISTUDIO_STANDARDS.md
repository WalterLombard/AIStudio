# AIStudio Development Standards

Version: 1.0

---

# Purpose

This document defines the engineering, architectural, coding, prompting and testing standards used throughout AIStudio.

Every agent, service and model must follow these standards.

The goal is consistency, maintainability and production-quality code.

---

# Project Philosophy

AIStudio is built as though it were a professional film production studio.

Every AI performs one specialised job.

No AI performs multiple unrelated responsibilities.

Agents cooperate through ProjectState.

---

# Core Principles

1. Single Responsibility Principle

Each agent performs exactly one task.

Example:

Executive Producer
Researcher
Outline
Script Writer
Storyboard
Visual Director

Never merge responsibilities.

---

2. JSON First

Every LLM interaction returns JSON.

Never parse natural language.

Never scrape text.

---

3. Strong Typing

Every JSON response is converted into a Pydantic model immediately.

No dictionaries should exist beyond the LLM boundary.

---

4. ProjectState

Every agent receives:

ProjectState

Every agent returns:

ProjectState

Agents never return raw JSON.

---

5. Prompt Driven

Business logic belongs inside prompts whenever possible.

Python should orchestrate.

LLMs should create.

---

6. Thin Agents

Agents should contain almost no business logic.

Agents should:

Load Prompt

Serialize Models

Call LLM

Validate JSON

Store Result

Return ProjectState

---

7. Shared Services

Shared functionality belongs in:

shared/services

Never duplicate functionality.

---

# Folder Structure

agents/

shared/

tests/

config/

docs/

---

# Prompt Standard

Every prompt follows the same structure.

ROLE

MISSION

SUCCESS CRITERIA

CREATIVE RULES

TECHNICAL RULES

INPUT

OUTPUT

VALIDATION

No exceptions.

---

# Coding Standard

Use Python 3.13+

Use type hints everywhere.

Use dataclasses only where appropriate.

Prefer Pydantic models.

Never use wildcard imports.

Never use magic numbers.

Prefer descriptive variable names.

---

# Logging Standard

Every service logs:

Request

Response

Errors

Validation

Never log huge context arrays.

Never log internal chain of thought.

---

# Error Handling

Raise custom exceptions.

Never swallow exceptions.

Errors should explain:

What happened

Where

Why

How to fix

---

# Testing

Every agent has:

test_<agent>.py

Tests verify:

JSON validity

Pydantic validation

ProjectState updates

Pipeline compatibility

---

# Prompt Rules

Never request markdown.

Never request explanations.

Always request valid JSON.

Always define required fields.

Always define allowed values.

Always define output schema.

---

# Agent Pipeline

Executive Producer

↓

Research

↓

Outline

↓

Script

↓

Storyboard

↓

Visual Director

↓

Video Generator

↓

QA

↓

Publisher

---

# Code Quality

Readable over clever.

Explicit over implicit.

Simple over complex.

Consistency over personal preference.

Every file should be understandable by a developer opening it for the first time.

---

# Future Goal

AIStudio should eventually resemble a real production studio where each AI is a specialist that contributes to a single high-quality documentary pipeline.