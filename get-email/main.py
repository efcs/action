import os
import sys
from pathlib import Path
from typing import Any, Literal

import actions_toolkit.core  as core
from actions_toolkit.github import Context
from github import Github
from pydantic import BaseModel, Field
import requests
import rich

rich.print(os.environ)

# Create Github instance with provided token
github = Github()


# Get current context (GitHub Actions context)
context = Context()
import rich
rich.inspect(context, methods=True)

# Fetch the repository information
repo = github.get_repo("efcs/action")


def get_commits():
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': os.environ['GITHUB_TOKEN'],
        'X-GitHub-Api-Version': '2022-11-28'
    }
    rich.print(os.environ['PULL_REQUEST_COMMITS_HREF'])
    url = os.environ['PULL_REQUEST_COMMITS_HREF']

    response = requests.get(url, headers=headers)
    rich.print(response)
    response.raise_for_status()
    return response.json()


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
    rich.print(os.environ)
    rich.print(context)
    get_commits()


if __name__ == "__main__":
    main()
