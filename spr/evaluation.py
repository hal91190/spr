import csv
import datetime
import logging
import os
import re
import subprocess
from dataclasses import dataclass, fields
from typing import Any

from spr.cistats import CommitsStats, collect_commits_stats_from_repository
from spr.config import CONFIG
from spr.grade import Grade
from spr.student import Student

NO_NUMBER = "NO_NUMBER"
NO_LASTNAME = "NO_LASTNAME"
NO_FIRSTNAME = "NO_FIRSTNAME"


@dataclass(init=False)
class Evaluation:
    """Result of the evaluation of a repository for a student."""

    number: str
    "Student number"

    lastname: str
    "Student lastname"

    firstname: str
    "Student firstname"

    github_username: str
    "Github username of the student"

    repository_name: str
    "Name of the repository"

    repository_url: str
    "URL of the repository"

    nb_commits: int
    "Number of commits"

    first_commit_datetime: datetime.datetime
    "Timestamp of the first commit"

    last_commit_datetime: datetime.datetime
    "Timestamp of the last commit"

    min_time_between_commits: int
    "Minimum time between 2 commits (s)"

    avg_time_between_commits: int
    "Average time between 2 commits (s)"

    avg_msg_length: int
    "Average length of commit messages"

    evaluations: list[int]
    "Result of the evaluations"

    def __init__(
        self, student: Student, grade: Grade, ci_stats: CommitsStats, result: list[int]
    ):
        """Create an evaluation from a student, a grade, stats about commits and a result."""
        self.number = student.number
        self.lastname = student.lastname
        self.firstname = student.firstname
        self.github_username = grade.github_username
        self.repository_name = grade.repository_name
        self.repository_url = grade.repository_url
        self.nb_commits = ci_stats.nb_commits
        self.first_commit_datetime = ci_stats.first_commit_datetime
        self.last_commit_datetime = ci_stats.last_commit_datetime
        self.min_time_between_commits = ci_stats.min_time_between_commits
        self.avg_time_between_commits = ci_stats.avg_time_between_commits
        self.avg_msg_length = ci_stats.avg_msg_length
        self.evaluations = result

    def __getitem__(self, index: int) -> Any:
        """Access to attributes by index.

        Args:
            index (int): index of the attribute

        Returns:
            Any: the value of the attribute
        """
        attributes = {k: v for k, v in vars(self).items() if k != "evaluations"}
        values = list(attributes.values()) + self.evaluations
        return values[index]

    @classmethod
    def headers(cls) -> list[str]:
        """Get the headers for evaluations."""
        headers = [f.name for f in fields(cls) if f.name != "evaluations"]
        for cmd in CONFIG.commands:
            headers.append(cmd["name"])
            if cmd["regex"]:
                nb_groups = re.compile(cmd["regex"]).groups
                headers.extend([f"{cmd['name']}_{i}" for i in range(nb_groups)])
        return headers


def evaluate_repositories(
    students: list[Student], grades: list[Grade]
) -> list[Evaluation]:
    """Run a list of commands in students repositories and collect results."""
    logger = logging.getLogger(__name__)
    evaluations = []
    for grade in grades:
        student = find_student_with_grade(grade, students)
        if os.path.isdir(grade.repository_name):
            logger.info("Evaluating %s for %s", grade.repository_name, student)
            ci_stats = collect_commits_stats_from_repository(grade.repository_name)
            result = evaluate_repository(student, grade.repository_name)
            evaluations.append(Evaluation(student, grade, ci_stats, result))
        else:
            logger.fatal("No directory named %s", grade.repository_name)
    return evaluations


def evaluate_repository(student: Student, repository_path: str) -> list[int]:
    """Run a list of commands in a repository and return the number of successful commands."""
    logger = logging.getLogger(__name__)
    current_working_directory = os.getcwd()
    os.chdir(repository_path)
    environment = os.environ.copy() | CONFIG.environment
    result = []
    for command in CONFIG.commands:
        result.extend(execute_command(command, environment))
    logger.info("Result for %s = %s", student, result)
    os.chdir(current_working_directory)
    return result


def execute_command(command: dict[str, Any], environment: dict[str, str]) -> list[int]:
    """Run a command and get a result."""
    logger = logging.getLogger(__name__)
    stdout_redir = subprocess.DEVNULL
    stderr_redir = subprocess.DEVNULL
    if command["regex"]:
        stdout_redir = subprocess.PIPE
        stderr_redir = subprocess.STDOUT
    completed_process = subprocess.run(
        command["cmd"],
        stdout=stdout_redir,
        stderr=stderr_redir,
        env=environment,
    )
    result = [1] if completed_process.returncode == 0 else [0]
    found_groups = None
    if command["regex"]:
        for line in completed_process.stdout.decode().split("\n"):
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


def find_student_with_grade(grade: Grade, students: list[Student]) -> Student:
    """Find a student in the list of students from the identifier in the grade."""
    logger = logging.getLogger(__name__)
    # match grade with student list
    student_from_grade = grade.extract_student()
    matching_students = list(
        filter(lambda s: s.number == student_from_grade.number, students)
    )
    student = Student(NO_NUMBER, NO_LASTNAME, NO_FIRSTNAME)
    if len(matching_students) == 0:
        logger.warning("No matching student for %s", student_from_grade)
    elif len(matching_students) > 1:  # many matching students
        logger.warning(
            "More than one matching student for %s : %s",
            student_from_grade,
            matching_students,
        )
    else:  # OK, only one student
        student = matching_students[0]
        logger.debug("Matching found for %s : %s", student_from_grade, student)
    return student


def write_evaluations(evaluations: list[Evaluation], evaluations_filename: str) -> None:
    with open(evaluations_filename, "w", newline="") as evaluations_file:
        evaluations_writer = csv.writer(evaluations_file)
        evaluations_writer.writerow(Evaluation.headers())
        evaluations_writer.writerows(evaluations)  # type: ignore
