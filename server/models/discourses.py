from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from server.models.discourse_items import DiscourseItem
from server.models.discourse_items_links import DiscourseItemsLink


class Action(str, Enum):
    add: str = 'add'
    delete: str = 'delete'


class UpdateType(str, Enum):
    discourseItem: str = 'discourseItem'
    discourseItemsLink: str = 'discourseItemsLink'


class Discourse(BaseModel):
    discourseItems: List[DiscourseItem] = Field(...)
    discourseItemsLinks: Optional[List[DiscourseItemsLink]] = Field(None)

    class Config:
        schema_extra = {
            'example': {
                'discourseItems': [
                        {
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
                ],
                'discourseItemsLinks': [
                    {
                        'sourceId': '603527d6e1b3b909c07ad834',
                        'targetId': '603527d6e1b3b909c07ad834',
                        'type':'normal'
                    },
                    {
                        'sourceId': '603527d6e1b3b909c07ad834',
                        'targetId': '603527d6e1b3b909c07ad834',
                        'type': 'normal'
                    }
                ]
            }
        }


class UpdateDiscourseAddDiscourseItem(BaseModel):
    discourseItem: DiscourseItem = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'discourseItem': {
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
                'discourseItemsLinks': {
                    'sourceId': '603527d6e1b3b909c07ad834',
                    'targetId': '603527d6e1b3b909c07ad834',
                    'type': 'normal'
                },
                'id': '6036a279f5ab842234175f15'
            }
        }


class UpdateDiscourseAddDiscourseItemsLink(BaseModel):
    discourseItemsLink: DiscourseItemsLink = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'discourseItemsLinks': {
                    'sourceId': '603527d6e1b3b909c07ad834',
                    'targetId': '603527d6e1b3b909c07ad834',
                    'type': 'normal'
                }
            }
        }


class UpdateDiscourseDeleteDiscourseItemOrLink(BaseModel):
    id: str = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'id': '6036a279f5ab842234175f15'
            }
        }
