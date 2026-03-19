from dataclasses import dataclass
import logging
import csv

from spr.student import Student


@dataclass(frozen=True)
class Grade:
    """Identifies a repository for students."""

    roster_identifier: str
    "Name and number of a student"

    github_username: str
    "Github username of the student"

    repository_name: str
    "Name of the repository"

    repository_url: str
    "URL of the repository"

    def extract_student(self) -> Student:
        """Extract student information from the grade.

        The field `roster_identifier` is expected to be in the format `lastname,firstname,number`.

        Returns:
            Student: a student description
        """
        logger = logging.getLogger(__name__)
        identifier = [part.strip() for part in self.roster_identifier.split(",")]
        number, firstname, lastname = "NO_NUMBER", "NO_FIRSTNAME", "NO_LASTNAME"
        if len(identifier) < 2:
            logger.warning(
                "Not enough information in roster identifier [%s]",
                self.roster_identifier,
            )
        else:
            lastname = identifier[0] or lastname
            firstname = identifier[1] or firstname
            if len(identifier) == 2:
                logger.warning(
                    "No student number in roster identifier [%s]",
                    self.roster_identifier,
                )
            else:
                number = identifier[2] or number
        logger.debug("Student extracted (%s, %s, %s)", number, lastname, firstname)
        return Student(number, lastname, firstname)


def load_grades(grades_filename: str) -> list[Grade]:
    """Load the list of grades from a csv file coming from github classroom.

    Attributes are : "assignment_name","assignment_url","starter_code_url","github_username",
                     "roster_identifier","student_repository_name","student_repository_url",
                     "submission_timestamp","points_awarded","points_available"

    Parameters:
        grades_filename (str): a csv file from github classroom

    Returns:
        (list[Grade]): the list of repositories
    """
    grades: list[Grade] = []

    try:
        with open(grades_filename, newline="", encoding="utf-8-sig") as grades_file:
            grades_reader = csv.reader(grades_file, delimiter=",", quotechar='"')
            if next(grades_reader, None) is None:  # skip header, handle empty file
                raise ValueError(
                    f"Grades file '{grades_filename}' is empty or missing header"
                )

            for row in grades_reader:
                grades.append(Grade(row[4], row[3], row[5], row[6]))

    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Grades file '{grades_filename}' not found. Need the list of grades as a CSV file from Github Classroom"
        ) from e

    return grades
