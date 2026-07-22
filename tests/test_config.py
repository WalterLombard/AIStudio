from shared.config import config


def test_config_loading():
    print("\nApplication")
    print("----------------")
    print(f"Name    : {config.application.name}")
    print(f"Version : {config.application.version}")

    print("\nLLM")
    print("----------------")
    print(f"Provider: {config.models.llm.provider}")
    print(f"Model   : {config.models.llm.model}")

    print("\nImage")
    print("----------------")
    print(f"Model   : {config.models.image.model}")

    print("\nVideo")
    print("----------------")
    print(f"Model   : {config.models.video.model}")

    print("\nProjects Folder")
    print("----------------")
    print(f"Path    : {config.paths.projects}")


if __name__ == "__main__":
    test_config_loading()