"""
AIStudio Outline Agent Test

Pipeline

Executive Producer
        ↓
Research
        ↓
Outline

This test verifies that the Outline Agent correctly produces an
OutlineData object and stores it in the ProjectState.
"""

from __future__ import annotations

import json

from agents.executive_producer.agent import ExecutiveProducer
from agents.researcher.agent import ResearchAgent
from agents.outline.agent import OutlineAgent


print("=" * 80)
print("AISTUDIO OUTLINE AGENT TEST")
print("=" * 80)

#
# Executive Producer
#

producer = ExecutiveProducer()

state = producer.run(
    "Create a ten minute documentary about sharks."
)

#
# Research
#

researcher = ResearchAgent()

state = researcher.run(state)

#
# Outline
#

outliner = OutlineAgent()

state = outliner.run(state)

print()
print("=" * 80)
print("PROJECT STATE")
print("=" * 80)

print(

    json.dumps(

        state.model_dump(

            mode="json"

        ),

        indent=4,

        ensure_ascii=False,

    )

)