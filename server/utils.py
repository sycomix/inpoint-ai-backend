import json
import requests
from bs4 import BeautifulSoup #beautifulsoup4==4.9.3


def remove_html(text):
    """
    Function which strips HTML tags and unescapes HTML symbols from text.
    """
    return BeautifulSoup(html.unescape(text), features = 'html.parser').get_text(strip = True)


def get_data_from_ergologic():
    """
    Function which GETs data from the Ergologic backend.
    """
    workspaces_url = 'http://fc.ergologic.gr:8041/wspSpaces.php'
    discussions_url = 'http://fc.ergologic.gr:8041/wspDiscussions.php'
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
         'Position': wsp['Position'],
         'DiscussionText': remove_html(wsp['DiscussionText'])
        } for wsp in discussions_json
    ]
    return