from dataclasses import dataclass
import json

CONFIG_FILENAME = "spr.json"


@dataclass(frozen=True)
class Config:
    """Configuration options for the script."""

    students: str
    "CSV file with the list of students coming from MonDossierWeb"

    grades: str
    "CSV file with the list of grades coming from github classroom"

    evaluations: str
    "CSV file to output evaluations"

    environment: dict[str, str]
    "List of environment variables"

    commands: list[list[str]]
    "List of commands to execute to evaluate each repository"


def load_config(filename: str) -> Config:
    """Load the configuration from a json file."""
    with open(filename, "r") as file:
        config_json = json.load(file)

    return Config(**config_json)


CONFIG = load_config(CONFIG_FILENAME)
