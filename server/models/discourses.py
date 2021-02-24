from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from server.models.discourse_items import DiscourseItem

class Purpose(str, Enum):
    add: str = 'add'
    delete: str = 'delete'
    update: str = 'update'

class Discourse(BaseModel):
    discourse_items: List[DiscourseItem] = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'discourse_items': [
                        {
                            'userId': "603527d6e1b3b909c07ad834",
                            'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum lorem '
                                    'dolor, sit amet porta velit pellentesque vitae. Pellentesque viverra eu mi vitae '
                                    'porta. Nam arcu libero, laoreet vitae lacus id, condimentum tincidunt mi. '
                                    'Maecenas sem diam, pulvinar id gravida at, lacinia ac odio. Donec elit lacus, '
                                    'iaculis id suscipit in, sollicitudin vel ex. Nunc feugiat, felis et ullamcorper '
                                    'commodo, arcu erat gravida tortor, sit amet feugiat lectus dolor sit amet magna. '
                                    'Mauris nec dapibus elit, sed auctor lacus.',
                            'parentId': '603527d6e1b3b909c07ad834'
                        },
                        {
                            'userId':"603527d6e1b3b909c07ad834",
                            'text':'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum lorem '
                                   'dolor, sit amet porta velit pellentesque vitae. Pellentesque viverra eu mi vitae '
                                   'porta. Nam arcu libero, laoreet vitae lacus id, condimentum tincidunt mi. '
                                   'Maecenas sem diam, pulvinar id gravida at, lacinia ac odio. Donec elit lacus, '
                                   'iaculis id suscipit in, sollicitudin vel ex. Nunc feugiat, felis et ullamcorper '
                                   'commodo, arcu erat gravida tortor, sit amet feugiat lectus dolor sit amet magna. '
                                   'Mauris nec dapibus elit, sed auctor lacus.',
                            'parentId':'603527d6e1b3b909c07ad834'
                        }
                ]
            }
        }

class UpdateDiscourse(BaseModel):
    purpose: Purpose = Field(...)
    discourse_item: DiscourseItem = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'purpose': 'add',
                'discourse_item': {
                        'userId':"603527d6e1b3b909c07ad834",
                        'text':'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum lorem '
                               'dolor, sit amet porta velit pellentesque vitae. Pellentesque viverra eu mi vitae '
                               'porta. Nam arcu libero, laoreet vitae lacus id, condimentum tincidunt mi. '
                               'Maecenas sem diam, pulvinar id gravida at, lacinia ac odio. Donec elit lacus, '
                               'iaculis id suscipit in, sollicitudin vel ex. Nunc feugiat, felis et ullamcorper '
                               'commodo, arcu erat gravida tortor, sit amet feugiat lectus dolor sit amet magna. '
                               'Mauris nec dapibus elit, sed auctor lacus.',
                        'parentId':'603527d6e1b3b909c07ad834'
                }
            }
        }