#!/usr/bin/env python3

"""A script to evaluate a set of student repositories."""

import logging

from spr.config import CONFIG
from spr.student import load_students
from spr.grade import load_grades
from spr.evaluation import evaluate_repositories, write_evaluations


def main():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    logger.debug(CONFIG)

    students = load_students(CONFIG.students)
    logger.info("%d students loaded from csv file", len(students))
    logger.debug(students)

    grades = load_grades(CONFIG.grades)
    logger.info("%d grades loaded from csv file", len(grades))
    logger.debug(grades)

    evaluations = evaluate_repositories(students, grades)
    logger.debug(evaluations)
    write_evaluations(evaluations, CONFIG.evaluations)


if __name__ == "__main__":
    main()
