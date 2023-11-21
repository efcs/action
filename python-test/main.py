import actions_toolkit.core  as core
from pydantic import BaseModel, Field, RootModel
from typing import Literal, Any
import rich
import os
from pathlib import Path
import sys
from github import Github
from actions_toolkit.github import Context


rich.inspect(core)
rich.print(core)

core.save_state('time', 'new Date().toTimeString()')
core.set_output('result', 'This is the result')
core.info('Something went OK')

context = Context()

# First create a Github instance:
g = Github(os.environ['GITHUB_TOKEN'])

# Then play with your Github objects:
repo = g.get_repo("efcs/action")

commit = repo.get_commit(context.sha)




class TestResult(BaseModel):
  code: Literal["PASS", "FAIL", "SKIP", "XPASS"]
  elapsed: float
  metrics: dict[str, Any] = Field(default_factory=dict)
  name: str
  output: str

class LITTestResults(BaseModel):
  version: tuple[int, int, int] = Field(alias="__version__")
  elapsed: float
  tests: list[TestResult] = Field(default_factory=list)

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


rich.print(sys.argv)
in_data = Path(sys.argv[1]).read_text()
results = LITTestResults.model_validate_json(in_data)

rich.print(results)

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


annotations = conclusion, process_results(results)

check_run = repo.create_check_run(name="Libc++ Test Suite",
                                  head_sha=context.sha,
                                  status="completed",
                                  conclusion=conclusion,
                                  output={"title": "Check Run Output",
                                           "summary": f"{len(annotations)} tests failed.",
                                           "annotations": annotations})



