import os
import sys
from pathlib import Path
from typing import Any, Literal

import actions_toolkit.core  as  core
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


def process_results(results: LITTestResults):
    annotations = []
    conclusion = "success"

    for test in results.tests:
        if test.code == "FAIL":
            conclusion = "failure"
            path_name = test.name.split("::")[1].strip()
            path = Path('libcxx/test', path_name)

            annotation = {
                "path": str(path),
                "start_line": 1,
                "end_line": 1,
                "annotation_level": "failure",
                "message": f"Test {test.name} FAILED",
                "raw_details": test.output,
                "title": "Test Failure"
            }

            annotations.append(annotation)

    return conclusion, annotations


def main():
    input_file = sys.argv[1]
    results_file = Path(input_file).read_text()
    results = LITTestResults.model_validate_json(results_file)

    rich.print(results)

    conclusion, annotations = process_results(results)

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

if __name__ == "__main__":
    main()
