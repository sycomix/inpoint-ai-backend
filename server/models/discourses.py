from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from server.models.discourse_items import DiscourseItem


class Purpose(str, Enum):
    add: str = 'add'
    delete: str = 'delete'


class Discourse(BaseModel):
    discourseItems: List[DiscourseItem] = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'discourseItems': [
                        {
                            'parentId': '603527d6e1b3b909c07ad834',
                            'label': 'issue 1',
                            'type': 'issue',
                            'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum lorem '
                                    'dolor, sit amet porta velit pellentesque vitae. Pellentesque viverra eu mi vitae '
                                    'porta. Nam arcu libero, laoreet vitae lacus id, condimentum tincidunt mi. '
                                    'Maecenas sem diam, pulvinar id gravida at, lacinia ac odio. Donec elit lacus, '
                                    'iaculis id suscipit in, sollicitudin vel ex. Nunc feugiat, felis et ullamcorper '
                                    'commodo, arcu erat gravida tortor, sit amet feugiat lectus dolor sit amet magna. '
                                    'Mauris nec dapibus elit, sed auctor lacus.',
                            'authorId': "603527d6e1b3b909c07ad834",
                            'likes': 4,
                            'dislikes': 3
                        },
                        {
                            'parentId': '603527d6e1b3b909c07ad834',
                            'label': 'issue 1',
                            'type': 'issue',
                            'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum lorem '
                                    'dolor, sit amet porta velit pellentesque vitae. Pellentesque viverra eu mi vitae '
                                    'porta. Nam arcu libero, laoreet vitae lacus id, condimentum tincidunt mi. '
                                    'Maecenas sem diam, pulvinar id gravida at, lacinia ac odio. Donec elit lacus, '
                                    'iaculis id suscipit in, sollicitudin vel ex. Nunc feugiat, felis et ullamcorper '
                                    'commodo, arcu erat gravida tortor, sit amet feugiat lectus dolor sit amet magna. '
                                    'Mauris nec dapibus elit, sed auctor lacus.',
                            'authorId': "603527d6e1b3b909c07ad834",
                            'likes': 4,
                            'dislikes': 3
                        }
                ]
            }
        }


class UpdateDiscourse(BaseModel):
    purpose: Purpose = Field(...)
    discourseItem: Optional[DiscourseItem] = Field(None)
    id: Optional[str] = Field(None)

    class Config:
        schema_extra = {
            'example': {
                'purpose': 'add',
                'discourseItem': {
                        'parentId': '603527d6e1b3b909c07ad834',
                        'label': 'issue 1',
                        'type': 'issue',
                        'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum lorem '
                                'dolor, sit amet porta velit pellentesque vitae. Pellentesque viverra eu mi vitae '
                                'porta. Nam arcu libero, laoreet vitae lacus id, condimentum tincidunt mi. '
                                'Maecenas sem diam, pulvinar id gravida at, lacinia ac odio. Donec elit lacus, '
                                'iaculis id suscipit in, sollicitudin vel ex. Nunc feugiat, felis et ullamcorper '
                                'commodo, arcu erat gravida tortor, sit amet feugiat lectus dolor sit amet magna. '
                                'Mauris nec dapibus elit, sed auctor lacus.',
                        'authorId': "603527d6e1b3b909c07ad834",
                        'likes': 4,
                        'dislikes': 3
                },
                'id': '6036a279f5ab842234175f15'
            }
        }