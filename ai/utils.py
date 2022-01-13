import sys
import time
import html
import spacy
import fasttext
import functools
import requests
from bs4 import BeautifulSoup
from decouple import config

import ai.config

ERGOLOGIC_WORKSPACES_URL = config('ERGOLOGIC_WORKSPACES_URL')
ERGOLOGIC_DISCUSSIONS_URL = config('ERGOLOGIC_DISCUSSIONS_URL')

class Models:
    __en_nlp = None
    __el_nlp = None
    __ang_det = None

    @classmethod
    def load_models(cls):
        """
        Class method which loads the english & greek
        NLP models, as well as the language detection model.
        This needs to run once since all models need a few seconds to load.
        """
        if cls.__en_nlp is None:
            cls.__en_nlp = spacy.load('en_core_web_lg')
            cls.__el_nlp = spacy.load('el_core_news_lg')
            cls.__ang_det = fasttext.load_model('/downloads/lid.176.bin')

        return (
            cls.__en_nlp,
            cls.__el_nlp,
            cls.__ang_det
        )


def detect_language(model, text):
    """
    Function that detects the language of a given text,
    using the fasttext algorithm.
    """
    language = model.predict(text, k = 1)[0][0]  # Top 1 matching language.
    
    if language == '__label__en':
        return 'english'
    elif language == '__label__el':
        return 'greek'
    elif ai.config.debug:
        print(f'{text} -> Unsupported language {language}', file = sys.stderr)


def remove_greek_accents(text):
    """
    Function which replaces all greek accented characters
    with non-accented ones.
    """
    gr_accents = {'ά': 'α', 'ό': 'ο', 'ύ': 'υ', 'ί': 'ι', 'έ': 'ε', 'ϊ': 'ι'}
    return ''.join(c if c not in gr_accents else gr_accents[c] for c in text)


def remove_html(text):
    """
    Function which strips HTML tags and unescapes HTML symbols from text.
    """
    return BeautifulSoup(html.unescape(text), features = 'html.parser').get_text(strip = True)


def preprocess(text, nlp, language):
    """
    Function which removes all stopwords,
    pronouns and punctuation from the text.
    """
    # Create the document from the lowercased text.
    doc = list(nlp.pipe([text], disable = ['parser', 'ner', 'textcat']))

    # Isolate the useful tokens and join them using a single space.
    if language == 'english':
        return ' '.join(
            token.text.lower() for token in doc[0]
            if token.text not in nlp.Defaults.stop_words
            and token.pos_ in ['NOUN', 'PROPN'] and not token.is_punct
        )
    elif language == 'greek':
        return ' '.join(
            remove_greek_accents(token.text.lower()) for token in doc[0]
            if token.text not in nlp.Defaults.stop_words
            and token.pos_ in ['NOUN', 'PROPN'] and not token.is_punct
        )


def remove_stopwords_from_keyphrases(keyphrases, nlp):
    """
    Function which removes all stopwords,
    from the keyphrases after they have been formed.
    """
    return [
        ' '.join(
            word for word in keyphrase.split()
            if word.lower() not in nlp.Defaults.stop_words
        ) for keyphrase in keyphrases
    ]
            

def counter(func):
    """
    Print the elapsed system time in seconds, 
    if only the debug flag is set to True.
    """
    if not ai.config.debug:
        return func
    @functools.wraps(func)
    def wrapper_counter(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f'{func.__name__}: {end_time - start_time} secs')
        return result
    return wrapper_counter


def get_data_from_ergologic():
    """
    Function which GETs data from the Ergologic backend.
    """
    workspaces_url = ERGOLOGIC_WORKSPACES_URL
    discussions_url = ERGOLOGIC_DISCUSSIONS_URL

    try:
        workspaces_json = requests.get(workspaces_url).json()
        discussions_json = requests.get(discussions_url).json()
    except Exception as e:
        raise e

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
         'Position': ai.config.position_number_to_string.get(wsp['Position'], 'Issue'),
         'DiscussionText': remove_html(wsp['DiscussionText'])
        } for wsp in discussions_json
    ]
    return (workspaces, discussions)