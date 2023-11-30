from pydantic import BaseModel, Field
from typing import Literal, Any, Union, Optional


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
