import os
import sys
from pathlib import Path
from typing import Any, Literal

import actions_toolkit.core  as core
from actions_toolkit.github import Context
from github import Github
from pydantic import BaseModel, Field
import rich


# Create Github instance with provided token
github_token = os.environ["GITHUB_TOKEN"]
github = Github(github_token)

# Get current context (GitHub Actions context)
context = Context()

# Fetch the repository information
repo = github.get_repo("efcs/action")
commit = repo.get_commit(context.sha)
rich.inspect(commit)
rich.print(commit)


class Annotation(BaseModel):
    path: str
    start_line: int
    end_line: int
    annotation_level: Literal["notice", "warning", "failure"]
    message: str
    title: str
    raw_details: str

class CheckRun(BaseModel):
    name: str
    head_sha: str
    status: Literal["queued", "in_progress", "completed"]
    conclusion: Literal["success", "failure", "neutral", "cancelled", "timed_out", "action_required"]
    output: dict[str, Any] = Field(default_factory=dict)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    check_suite: dict[str, Any] = Field(default_factory=dict)
    external_id: str
    started_at: str
    completed_at: str
    output: dict[str, Any] = Field(default_factory=dict)
    annotations: list[Annotation] = Field(default_factory=list)
    pull_requests: list[dict[str, Any]] = Field(default_factory=list)



def main():
    rich.print(context)
    '''
    check_run = repo.create_check_run(
        name="Libc++ Test Suite",
        head_sha=context.sha,
        status="completed",
        conclusion=conclusion,
        output={
            "title": "Check Run Output",
            "summary": f"{len(annotations)} tests failed.",
            "annotations": annotations
        },
    )
    rich.print(check_run)
    '''


if __name__ == "__main__":
    main()
