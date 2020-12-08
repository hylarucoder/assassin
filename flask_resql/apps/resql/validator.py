from typing import NewType

from pydantic import BaseModel

UserId = NewType('UserId', int)


class Validator(BaseModel):
    ...
