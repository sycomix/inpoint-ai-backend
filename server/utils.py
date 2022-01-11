import json
import requests
from bs4 import BeautifulSoup
import html
from decouple import config

ERGOLOGIC_WORKSPACES_URL = config('ERGOLOGIC_WORKSPACES_URL')
ERGOLOGIC_DISCUSSIONS_URL = config('ERGOLOGIC_DISCUSSIONS_URL')

position_number_to_string = {
    -2: 'Solution',
    -1: 'Position-against',
    0: 'Note',
    1: 'Position-in-favor',
    2: 'Issue',
}

def remove_html(text):
    """
    Function which strips HTML tags and unescapes HTML symbols from text.
    """
    return BeautifulSoup(html.unescape(text), features = 'html.parser').get_text(strip = True)


def get_data_from_ergologic():
    """
    Function which GETs data from the Ergologic backend.
    """
    workspaces_url = ERGOLOGIC_WORKSPACES_URL
    discussions_url = ERGOLOGIC_DISCUSSIONS_URL
    workspaces_json = requests.get(workspaces_url).json()
    discussions_json = requests.get(discussions_url).json()

    workspaces = [
        {'id': wsp['id'],
         'OwnerId': wsp['OwnerId'],
         'Description': remove_html(wsp['Description']),
         'Summary': remove_html(wsp['Summary'])
        } for wsp in workspaces_json
    ]

    discussions = [
        {'id': wsp['id'],
         'SpaceId': wsp['SpaceId'],
         'UserId': wsp['UserId'],
         'Position': position_number_to_string.get(wsp['Position'], 'Issue'),
         'DiscussionText': remove_html(wsp['DiscussionText'])
        } for wsp in discussions_json
    ]
    return (workspaces, discussions)