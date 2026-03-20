from dataclasses import dataclass
import logging
import os
import datetime

from git import Repo  # type: ignore

DEFAULT_BRANCH = "main"
GITHUB_COMMITTER_NAME = "GitHub"
A_VERY_LONG_DURATION = datetime.timedelta(days=365 * 100)  # 100 years


@dataclass(frozen=True)
class CommitsStats:
    """Stats about commits in a git repository."""

    nb_commits: int
    "Number of commits"

    nb_commits_in_ranges: list[int]
    "Number of commits in each ranges defined in the config file"

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


@dataclass
class TmpCommitsStats:
    """Stats about commits in a git repository."""

    nb_commits: int
    "Number of commits"

    nb_commits_in_ranges: list[int]
    "Number of commits in each ranges defined in the config file"

    first_commit_datetime: datetime.datetime
    "Timestamp of the first commit"

    last_commit_datetime: datetime.datetime
    "Timestamp of the last commit"

    min_time_between_commits: float
    "Minimum time between 2 commits (s)"

    sum_time_between_commits: float
    "Sum of time between 2 commits (s)"

    sum_msg_length: int
    "Sum of lengths of commit messages"

    def __repr__(self):
        return f"TmpCommitsStats({self.nb_commits}, {self.nb_commits_in_ranges}, {self.first_commit_datetime}, {self.last_commit_datetime}, {self.min_time_between_commits}, {self.sum_time_between_commits}, {self.sum_msg_length})"

    def compute_avg_time_between_commits(self) -> float:
        """Compute the average time between commits."""
        return self.sum_time_between_commits / (
            self.nb_commits - 1 if self.nb_commits > 1 else 1
        )

    def compute_avg_msg_length(self) -> float:
        """Compute the average length of commit messages."""
        return self.sum_msg_length / (self.nb_commits if self.nb_commits > 0 else 1)

    def to_commits_stats(self) -> CommitsStats:
        """Convert to a CommitsStats object."""
        return CommitsStats(
            self.nb_commits,
            self.nb_commits_in_ranges,
            self.first_commit_datetime,
            self.last_commit_datetime,
            int(self.min_time_between_commits if self.nb_commits >= 2 else 0),
            int(self.compute_avg_time_between_commits()),
            int(self.compute_avg_msg_length()),
        )


def is_a_git_repository(path: str | os.PathLike) -> bool:
    """Check if a path is a git repository."""
    return os.path.isdir(os.path.join(path, ".git"))


def collect_commits_stats_from_repository(
    repository_path: str | os.PathLike,
    ci_ranges: list[tuple[datetime.datetime, datetime.datetime]],
) -> CommitsStats:
    """Collect stats about commits in a git repository"""
    logger = logging.getLogger(__name__)
    repository = Repo(repository_path)
    now = datetime.datetime.now()
    tmp_ci_stat = TmpCommitsStats(
        0, [0] * len(ci_ranges), now, now, float("Infinity"), 0.0, 0
    )

    previous_commit = None
    for commit in repository.iter_commits(DEFAULT_BRANCH):
        if commit.committer.name == GITHUB_COMMITTER_NAME:
            continue
        logger.debug(
            "Commit: %s, %s, %s (%d)",
            commit.author,
            commit.authored_datetime,
            commit.message,
            len(commit.message),
        )
        if tmp_ci_stat.nb_commits == 0:
            tmp_ci_stat.last_commit_datetime = (
                commit.authored_datetime
            )  # most recent commit

        time_between = (
            previous_commit.authored_datetime - commit.authored_datetime
            if previous_commit
            else A_VERY_LONG_DURATION
        )
        logger.debug(
            "Time between %s and %s = %s (%d)",
            commit.authored_datetime,
            previous_commit.authored_datetime
            if previous_commit
            else datetime.timedelta(),
            time_between,
            time_between.total_seconds(),
        )

        tmp_ci_stat.nb_commits += 1

        for i, (start, end) in enumerate(ci_ranges):
            if start <= commit.authored_datetime <= end:
                tmp_ci_stat.nb_commits_in_ranges[i] += 1

        tmp_ci_stat.first_commit_datetime = commit.authored_datetime
        tmp_ci_stat.sum_msg_length += len(commit.message)
        tmp_ci_stat.min_time_between_commits = (
            min(tmp_ci_stat.min_time_between_commits, time_between.total_seconds())
            if previous_commit
            else float("Infinity")
        )
        tmp_ci_stat.sum_time_between_commits += (
            time_between.total_seconds() if previous_commit else 0.0
        )
        logger.debug("%s", tmp_ci_stat)
        previous_commit = commit
    ci_stats = tmp_ci_stat.to_commits_stats()
    logger.debug("%s", ci_stats)
    return ci_stats
