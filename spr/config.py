import json
from dataclasses import dataclass
from typing import Any

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

    ci_ranges: list[dict[str, Any]]
    "List of datetime ranges to count commits"

    commands: list[dict[str, Any]]
    "List of commands to execute to evaluate each repository"


def load_config(config_file: str = CONFIG_FILENAME) -> Config:
    """Load the configuration from a JSON file.

    Args:
        config_file: Path to the configuration file.

    Returns:
        Config object with validated settings.

    Raises:
        FileNotFoundError: If configuration file doesn't exist.
        ValueError: If JSON is invalid or required fields are missing.
    """

    try:
        with open(config_file, "r") as file:
            config_json = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing configuration file '{config_file}': {e}")

    # Validate required fields
    required_fields = {"students", "grades", "evaluations", "environment", "commands"}
    options_fields = {"ci_ranges"}
    json_fields = set(config_json.keys())
    missing_fields = required_fields - json_fields
    if missing_fields:
        raise ValueError(f"Missing required configuration fields: {missing_fields}")
    other_fields = json_fields - required_fields - options_fields
    if other_fields:
        raise ValueError(f"Unexpected fields in configuration: {other_fields}")

    return Config(**config_json)
