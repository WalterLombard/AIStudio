from abc import ABC, abstractmethod
from time import perf_counter

from shared.logger import get_logger
from shared.models import ProjectState


class BaseAgent(ABC):
    """
    Base class for every AI Studio agent.

    Every agent receives a ProjectState,
    performs one task,
    and returns the updated ProjectState.
    """

    def __init__(self, name: str):

        self.name = name

        self.logger = get_logger(name)

    def execute(self, project: ProjectState) -> ProjectState:

        self.logger.info("=" * 70)
        self.logger.info(f"Starting {self.name}")
        self.logger.info(f"Project: {project.project_id}")

        start = perf_counter()

        try:

            project = self.run(project)

            elapsed = perf_counter() - start

            self.logger.info(
                f"{self.name} completed successfully in "
                f"{elapsed:.2f} seconds."
            )

            return project

        except Exception as ex:

            self.logger.exception(
                 f"{self.name} failed."
        )

            raise

    @abstractmethod
    def run(self, project: ProjectState) -> ProjectState:
        """
        Agent implementation.
        """
        pass