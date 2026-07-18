"""
Tests the complete Storyboard Agent pipeline.
"""

from agents.executive_producer.agent import ExecutiveProducerAgent
from agents.researcher.agent import ResearchAgent
from agents.outline.agent import OutlineAgent
from agents.script_writer.agent import ScriptWriterAgent
from agents.storyboard.agent import StoryboardAgent

from shared.models import ProjectState


print("=" * 80)
print("AISTUDIO STORYBOARD AGENT TEST")
print("=" * 80)

state = ProjectState()

# ------------------------------------------------------------------
# Executive Producer
# ------------------------------------------------------------------

producer = ExecutiveProducerAgent()

state = producer.run(
    state,
    "Create a documentary about sharks."
)

# ------------------------------------------------------------------
# Research
# ------------------------------------------------------------------

researcher = ResearchAgent()

state = researcher.run(
    state
)

# ------------------------------------------------------------------
# Outline
# ------------------------------------------------------------------

outliner = OutlineAgent()

state = outliner.run(
    state
)

# ------------------------------------------------------------------
# Script
# ------------------------------------------------------------------

writer = ScriptWriterAgent()

state = writer.run(
    state
)

# ------------------------------------------------------------------
# Storyboard
# ------------------------------------------------------------------

storyboard = StoryboardAgent()

state = storyboard.run(
    state
)

print()
print("=" * 80)
print("STORYBOARD")
print("=" * 80)

print(

    state.storyboard.model_dump_json(

        indent=4

    )

)