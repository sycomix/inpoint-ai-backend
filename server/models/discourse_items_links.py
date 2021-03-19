from pydantic import BaseModel, Field
from typing import Optional


class DiscourseItemsLink(BaseModel):
    sourceId: str = Field(...)
    targetId: str = Field(...)
    type: str = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'sourceId': '603527d6e1b3b909c07ad834',
                'targetId': '603527d6e1b3b909c07ad834',
                'type': 'normal'
            }
        }


class UpdateDiscourseItemsLink(BaseModel):
    sourceId: Optional[str] = Field(None)
    targetId: Optional[str] = Field(None)
    type: Optional[str] = Field(None)

    class Config:
        schema_extra = {
            'example': {
                'sourceId': '603527d6e1b3b909c07ad834',
                'targetId': '603527d6e1b3b909c07ad834',
                'type': 'normal'
            }
        }