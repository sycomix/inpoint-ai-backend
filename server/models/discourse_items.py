from typing import Optional
from pydantic import BaseModel, Field


class DiscourseItem(BaseModel):
    label: str = Field(...)
    type: str = Field(...)
    text: str = Field(...)
    authorId: str = Field(...)
    likes: int = Field(...)
    dislikes: int = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'label': 'issue 1',
                'type': 'issue',
                'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum lorem dolor, '
                        'sit amet porta velit pellentesque vitae. Pellentesque viverra eu mi vitae porta. Nam arcu '
                        'libero, laoreet vitae lacus id, condimentum tincidunt mi. Maecenas sem diam, pulvinar id '
                        'gravida at, lacinia ac odio. Donec elit lacus, iaculis id suscipit in, sollicitudin vel ex. '
                        'Nunc feugiat, felis et ullamcorper commodo, arcu erat gravida tortor, sit amet feugiat '
                        'lectus dolor sit amet magna. Mauris nec dapibus elit, sed auctor lacus.',
                'authorId': "603527d6e1b3b909c07ad834",
                'likes': 4,
                'dislikes': 3
            }
        }


class UpdateDiscourseItem(BaseModel):
    label: Optional[str] = Field(None)
    type: Optional[str] = Field(None)
    text: Optional[str] = Field(None)
    authorId: Optional[str] = Field(None)
    likes: Optional[int] = Field(None)
    dislikes: Optional[int] = Field(None)

    class Config:
        schema_extra = {
            'example': {
                'label': 'issue 1',
                'type': 'issue',
                'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum lorem dolor, '
                        'sit amet porta velit pellentesque vitae. Pellentesque viverra eu mi vitae porta. Nam arcu '
                        'libero, laoreet vitae lacus id, condimentum tincidunt mi. Maecenas sem diam, pulvinar id '
                        'gravida at, lacinia ac odio. Donec elit lacus, iaculis id suscipit in, sollicitudin vel ex. '
                        'Nunc feugiat, felis et ullamcorper commodo, arcu erat gravida tortor, sit amet feugiat '
                        'lectus dolor sit amet magna. Mauris nec dapibus elit, sed auctor lacus.',
                'authorId': "603527d6e1b3b909c07ad834",
                'likes': 4,
                'dislikes': 3
            }
        }
