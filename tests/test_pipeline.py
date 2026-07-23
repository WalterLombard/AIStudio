"""
AIStudio Pipeline Test

Runs the complete AIStudio pipeline.

Author : AIStudio
"""

from shared.pipeline.runner import PipelineRunner


def main() -> None:

    runner = PipelineRunner()

    state = runner.run(
        "Create a 10 minute documentary about the Megalodon."
    )

    print()
    print("=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)
    print()

    print(state.model_dump_json(indent=4))


if __name__ == "__main__":

    main()