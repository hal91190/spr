import logging
import os
from pathlib import Path
import re
import subprocess
from typing import Any

from spr.config import Config
from spr.student import Student


def evaluate_repository(
    student: Student, repository_path: str, config: Config
) -> list[int]:
    """Run a list of commands in a repository and return the number of successful commands."""
    logger = logging.getLogger(__name__)
    environment = os.environ.copy() | config.environment
    result = []
    for command in config.commands:
        result.extend(execute_command(command, repository_path, environment))
    logger.info("Result for %s = %s", student, result)
    return result


def execute_command(
    command: dict[str, Any], path: str, environment: dict[str, str]
) -> list[int]:
    """Run a command and get a result."""
    logger = logging.getLogger(__name__)
    path_to_run = Path(".") / path
    stdout_redir = subprocess.DEVNULL
    stderr_redir = subprocess.DEVNULL
    if command["regex"]:
        stdout_redir = subprocess.PIPE
        stderr_redir = subprocess.STDOUT
    completed_process = subprocess.run(
        command["cmd"],
        cwd=path_to_run.resolve(),
        stdout=stdout_redir,
        stderr=stderr_redir,
        env=environment,
        text=True,
    )
    result = [1] if completed_process.returncode == 0 else [0]
    found_groups = None
    if command["regex"]:
        for line in completed_process.stdout.split("\n"):
            logger.debug("%s", line)
            match = re.search(command["regex"], line)
            if match:
                found_groups = match.groups()
                logger.debug("Found groups: %s", found_groups)
    logger.debug(
        "Running '%s' (%d) : %s", command, completed_process.returncode, found_groups
    )
    if found_groups:
        result.extend(list(map(int, found_groups)))
    return result
