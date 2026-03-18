import csv
from dataclasses import dataclass


@dataclass(frozen=True)
class Student:
    """Information about students."""

    number: str
    "Student number"

    lastname: str
    "Student lastname"

    firstname: str
    "Student firstname"


def load_students(students_filename: str) -> list[Student]:
    """Load the list of students from a csv file coming from MonDossierWeb.

    Attributes are : DOSSIER,NOM,PRÉNOM,NAISSANCE,MESSAGERIE,CODE,VERSION,ÉTAPE

    Parameters:
        students_filename (str): a csv file from MondossierWeb

    Returns:
        (list[Student]): the list of students
    """
    students: list[Student] = []
    try:
        with open(students_filename, newline="", encoding="utf-8-sig") as students_file:
            students_reader = csv.reader(students_file, delimiter=",", quotechar='"')
            if next(students_reader, None) is None:  # skip header, handle empty file
                raise ValueError(
                    "Students file '%s' is empty or missing header", students_filename
                )

            for row in students_reader:
                students.append(Student(row[0], row[1], row[2]))

    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Students file '{students_filename}' not found. Need the list of students as a CSV file from MonDossierWeb"
        ) from e

    return students
