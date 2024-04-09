import json
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

MAX_BODY_LEN = 6000
MAX_STR_LEN = 50


class IssueHeader(BaseModel):
    title: str = Field(max_length=MAX_STR_LEN)
    subtitle: Optional[str] = Field(default=None, max_length=MAX_STR_LEN)
    no: Optional[str] = Field(default=None, max_length=MAX_STR_LEN)
    date: Optional[str] = Field(default=None, max_length=MAX_STR_LEN)
    cost: Optional[str] = Field(default=None, max_length=MAX_STR_LEN)


class IssueFonts(BaseModel):
    header_title_pt: Optional[int] = 38
    header_subtitle_pt: Optional[int] = 14
    header_details_pt: Optional[int] = 10
    main_title_pt: Optional[int] = 16
    main_subtitle_pt: Optional[int] = 14
    main_text_pt: Optional[int] = 10


class IssuePage(BaseModel):
    bg: Optional[Literal["none", "bashcorpo_v5", "bashcorpo_v5_pale"]] = None
    size: Optional[Literal["a4", "a5", "demitab"]] = "a4"

    @field_validator("bg")
    @classmethod
    def set_to_none(cls, value):
        if value == "none":
            return None
        return value


class Issue(BaseModel):
    page: IssuePage
    header: IssueHeader
    body: str = Field(max_length=MAX_BODY_LEN)
    fonts: Optional[IssueFonts] = IssueFonts()

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
