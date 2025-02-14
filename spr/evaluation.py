from dataclasses import dataclass
from typing import Any
import logging
import csv
import os
import subprocess

from git import Repo

from spr.config import CONFIG
from spr.student import Student
from spr.grade import Grade


@dataclass(frozen=True)
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

    evaluation: int
    "Result of the evaluation"

    def __getitem__(self, index: int) -> Any:
        """Access to attributes by index.

        Args:
            index (int): index of the attribute

        Returns:
            Any: the value of the attribute
        """
        return list(vars(self).values())[index]


def evaluate_repositories(
    students: list[Student], grades: list[Grade]
) -> list[Evaluation]:
    """Run a list of command in students repositories and collect results."""
    logger = logging.getLogger(__name__)
    evaluations = []
    for grade in grades:
        # match grade with student list
        student_from_grade = grade.extract_student()
        matching_students = list(
            filter(lambda s: s.number == student_from_grade.number, students)
        )
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
        # evaluate repository
        repository_path = grade.repository_name
        if os.path.isdir(repository_path):
            repository = Repo(repository_path)
            nb_commits = len(list(repository.iter_commits("main")))
            logger.info(
                "Evaluating repository %s (%d commits) for %s",
                repository_path,
                nb_commits,
                student_from_grade,
            )
            current_working_directory = os.getcwd()
            os.chdir(repository_path)
            environment = os.environ.copy() | CONFIG.environment
            result = 0
            for command in CONFIG.commands:
                completed_process = subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=environment,
                )
                result += 1 if completed_process.returncode == 0 else 0
                logger.debug(
                    "Running '%s' from '%s' (%d)",
                    command,
                    repository_path,
                    completed_process.returncode,
                )
            logger.info("Result for %s = %d", student_from_grade, result)
            evaluations.append(
                Evaluation(
                    student_from_grade.number,
                    student_from_grade.lastname,
                    student_from_grade.firstname,
                    grade.github_username,
                    grade.repository_name,
                    grade.repository_url,
                    nb_commits,
                    result,
                )
            )
            os.chdir(current_working_directory)
        else:
            logger.fatal("No directory named %s", repository_path)
    return evaluations


def write_evaluations(evaluations: list[Evaluation], evaluations_filename: str) -> None:
    with open(evaluations_filename, "w", newline="") as evaluations_file:
        evaluations_writer = csv.writer(evaluations_file)
        evaluations_writer.writerows(evaluations)
