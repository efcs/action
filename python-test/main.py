import actions_toolkit.core  as core

import rich
rich.inspect(core)
rich.print(core)

core.save_state('time', 'new Date().toTimeString()')
core.set_output('result', 'This is the result')
core.info('Something went OK')
import os

from github import Github
from actions_toolkit.github import Context

context = Context()

# First create a Github instance:
g = Github(os.environ['GITHUB_TOKEN'])

# Then play with your Github objects:
repo = g.get_repo("efcs/action")

commit = repo.get_commit(context.sha)

check_run = repo.create_check_run(name="My Check Run",
                                  head_sha=context.sha,
                                  status="completed",
                                  conclusion="success",
                                  output={"title": "Check Run Output",
                                           "summary": "Check run summary",
                                           "text": "Check run detailed output"})


from pydantic import BaseModel, Field, RootModel
from typing import Literal, Any

class TestResult(BaseModel):
  code: Literal["PASS", "FAIL", "SKIP", "XPASS"]
  elapsed: float
  metrics: dict[str, Any] = Field(default_factory=dict)
  name: str
  output: str

class LITTestResults(BaseModel):
  __version__: str = Field(..., alias="__version__")
  elapsed: float
  tests: list[TestResult] = Field(default_factory=list)

from pathlib import Path
import sys
import rich
rich.print(sys.argv)
in_data = Path(sys.argv[1]).read_text()
results = LITTestResults.model_validate_json(in_data)
import rich
rich.print(results)
