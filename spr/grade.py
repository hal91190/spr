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

        Returns:
            Student: a student description
        """
        logger = logging.getLogger(__name__)
        identifier = self.roster_identifier.split(",")
        if len(identifier) < 2:
            logger.warning(
                "Not enough information in roster identifier [%s]",
                self.roster_identifier,
            )
            lastname = "NO_LASTNAME"
            firstname = "NO_FISRTNAME"
            number = "NO_NUMBER"
        else:
            assert len(identifier) <= 3
            lastname = identifier[0]
            firstname = identifier[1]
            if len(identifier) == 2:
                logger.warning(
                    "No student number in roster identifier [%s]",
                    self.roster_identifier,
                )
                number = "NO_NUMBER"
            else:
                number = identifier[2]
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
    grades = []
    with open(grades_filename) as grades_file:
        grades_reader = csv.reader(grades_file, delimiter=",", quotechar='"')
        grades_reader.__next__()  # ignore the header line
        for grade in grades_reader:
            grades.append(Grade(grade[4], grade[3], grade[5], grade[6]))
    return grades
