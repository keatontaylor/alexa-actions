#  Copyright (c) 2022.
#  All rights reserved to the creator of the following script/program/app, please do not
#  use or distribute without prior authorization from the creator.
#  Creator: Antonio Manuel Nunes Goncalves
#  Email: amng835@gmail.com
#  LinkedIn: https://www.linkedin.com/in/antonio-manuel-goncalves-983926142/
#  Github: https://github.com/DEADSEC-SECURITY

# Built-In Imports
from typing import Optional

# 3rd-Party Imports
from pydantic import BaseModel, Field

# Local Imports


class HaStateError(BaseModel):
    _error: bool = Field(default=True, alias='error', title='error')
    text: str


class HaState(BaseModel):
    _error: bool = Field(default=False, alias='error', title='error')
    event_id: Optional[str]
    suppress_confirmation: bool = Field(default=False)
    text: str
