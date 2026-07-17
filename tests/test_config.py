from shared.config import config


print()

print("Application")

print("----------------")

print(config.application.name)

print(config.application.version)

print()

print("LLM")

print("----------------")

print(config.models.llm.provider)

print(config.models.llm.model)

print()

print("Image")

print("----------------")

print(config.models.image.model)

print()

print("Video")

print("----------------")

print(config.models.video.model)

print()

print("Projects Folder")

print("----------------")

print(config.paths.projects)