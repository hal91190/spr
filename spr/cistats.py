from dataclasses import dataclass
import logging
import os
import datetime
import sys

from git import Repo  # type: ignore

DEFAULT_BRANCH = "main"
GITHUB_COMMITTER_NAME = "GitHub"


@dataclass(frozen=True)
class CommitsStats:
    """Stats about commits in a git repository."""

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

    def __repr__(self):
        return f"CommitsStats({self.nb_commits}, {self.first_commit_datetime}, {self.last_commit_datetime}, {self.min_time_between_commits}, {self.avg_time_between_commits}, {self.avg_msg_length})"


def collect_commits_stats_from_repository(
    repository_path: str | os.PathLike,
) -> CommitsStats:
    """Collect stats about commits in a git repository"""
    logger = logging.getLogger(__name__)
    repository = Repo(repository_path)
    nb_commits = 0
    now = datetime.datetime.now()
    (
        nb_commits,
        first_commit_datetime,
        last_commit_datetime,
        min_time_between_commits,
        sum_time_between_commits,
        sum_msg_length,
    ) = 0, now, now, sys.float_info.max, 0.0, 0
    previous_commit = None
    for commit in repository.iter_commits(DEFAULT_BRANCH):
        if commit.committer.name == GITHUB_COMMITTER_NAME:
            continue
        logger.debug(
            "Commit: %s, %s, %s (%d)",
            commit.author,
            commit.committed_datetime,
            commit.message,
            len(commit.message),
        )
        if nb_commits == 0:
            last_commit_datetime = commit.committed_datetime
        time_between = (
            previous_commit.committed_datetime - commit.authored_datetime
            if previous_commit
            else datetime.timedelta(days=999999)  # a very long duration
        )
        logger.debug(
            "Time between %s and %s = %s (%d)",
            commit.authored_datetime,
            previous_commit.committed_datetime
            if previous_commit
            else datetime.timedelta(),
            time_between,
            time_between.total_seconds(),
        )
        nb_commits += 1
        first_commit_datetime = commit.committed_datetime
        sum_msg_length += len(commit.message)
        min_time_between_commits = (
            min(min_time_between_commits, time_between.total_seconds())
            if previous_commit
            else sys.float_info.max
        )
        sum_time_between_commits += (
            time_between.total_seconds() if previous_commit else 0.0
        )
        logger.debug(
            "CommitsStats(%d, %s, %s, %d, %d, %d)",
            nb_commits,
            first_commit_datetime,
            last_commit_datetime,
            min_time_between_commits,
            sum_time_between_commits,
            sum_msg_length,
        )
        previous_commit = commit
    avg_msg_length = sum_msg_length / (nb_commits if nb_commits > 0 else 1)
    avg_time_between_commits = sum_time_between_commits / (
        nb_commits - 1 if nb_commits > 1 else 1
    )
    cstats = CommitsStats(
        nb_commits,
        first_commit_datetime,
        last_commit_datetime,
        int(min_time_between_commits),
        int(avg_time_between_commits),
        int(avg_msg_length),
    )
    logger.debug("%s", cstats)
    return cstats
