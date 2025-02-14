from dataclasses import dataclass
import csv


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
    students = []
    with open(students_filename) as students_file:
        students_reader = csv.reader(students_file, delimiter=",", quotechar='"')
        students_reader.__next__()  # ignore the header line
        for student in students_reader:
            students.append(Student(student[0], student[1], student[2]))
    return students
