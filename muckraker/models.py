from pydantic import BaseModel, Field
from typing import Optional, Literal

MAX_BODY_LEN = 6000
MAX_STR_LEN = 50


class IssueHeading(BaseModel):
    title: str = Field(max_length=MAX_STR_LEN)
    subtitle: Optional[str] = Field(default=None, max_length=MAX_STR_LEN)
    no: Optional[str] = Field(default=None, max_length=MAX_STR_LEN)
    date: Optional[str] = Field(default=None, max_length=MAX_STR_LEN)
    cost: Optional[str] = Field(default=None, max_length=MAX_STR_LEN)


class IssueConfig(BaseModel):
    bg: Optional[bool] = False
    size: Optional[Literal["a4", "a5", "demitab"]] = "a4"
    heading: IssueHeading


class Issue(BaseModel):
    config: IssueConfig
    body: str = Field(max_length=MAX_BODY_LEN)
