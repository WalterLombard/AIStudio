import json
from pathlib import Path


class ProjectService:

    def __init__(self):

        self.root = Path("projects")

    def create(self, project_name: str):

        project = self.root / project_name

        project.mkdir(parents=True, exist_ok=True)

        folders = [

            "research",

            "script",

            "storyboard",

            "visuals",

            "audio",

            "video",

            "exports",

            "cache"

        ]

        for folder in folders:

            (project / folder).mkdir(exist_ok=True)

        return project

    def save_json(

        self,

        project,

        relative_path,

        data

    ):

        file = project / relative_path

        file.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        with open(

            file,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                data,

                f,

                indent=4,

                ensure_ascii=False

            )

    def load_json(

        self,

        project,

        relative_path

    ):

        file = project / relative_path

        with open(

            file,

            encoding="utf-8"

        ) as f:

            return json.load(f)