import sys
import time
import html
import string
import spacy
import fasttext
import logging
import datetime
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
    __lang_det = None

    @classmethod
    def load_models(cls):
        """
        Class method which loads the english & greek
        NLP models, as well as the language detection model.
        This needs to run once since all models need a few seconds to load.
        """
        logging.info('Loading pre-trained ML models...')
        if cls.__en_nlp is None:
            cls.__en_nlp = spacy.load('en_core_web_lg')
            cls.__el_nlp = spacy.load('el_core_news_lg')
            cls.__lang_det = fasttext.load_model('/downloads/lid.176.bin')

        return (
            cls.__en_nlp,
            cls.__el_nlp,
            cls.__lang_det
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
    gr_accents = {'ά': 'α', 'ό': 'ο', 'ύ': 'υ', 'ί': 'ι', 'έ': 'ε', 'ϊ': 'ι', 'ή': 'η'}
    return ''.join(c if c not in gr_accents else gr_accents[c] for c in text)


def remove_html(text):
    """
    Function which strips HTML tags and unescapes HTML symbols from text.
    """
    return BeautifulSoup(html.unescape(text), features = 'html.parser').get_text(strip = True)


def remove_punctuation_and_whitespace(text):
    """
    Function which replaces punctuation with a space character 
    and then removes unnecessary whitespace characters.
    """
    text = text.translate (
        str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    )
    return ' '.join(text.split())


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


def remove_punctuation_and_whitespace_from_keyphrases(keyphrases):
    """
    Function which removes all punctuation and unnecessary whitespace,
    from the keyphrases after they have been formed.
    """
    return list(map(remove_punctuation_and_whitespace, keyphrases))


def remove_stopwords_from_keyphrases(keyphrases, nlp, language, only_prefixes = False):
    """
    Function which removes all stopwords or only the prefixed stopwords,
    from the keyphrases after they have been formed. Each keyphrase 
    is split on multiple prefixes and the minimum keyphrase 
    in terms of length is selected.
    """
    # Select the correct list of prefixes based on the language.
    prefixes = (
        ai.config.en_stopword_prefixes if language == 'english'
        else ai.config.el_stopword_prefixes
    )
    if only_prefixes:
        return [
            min((keyphrase.split(prefix, 1)[-1]
            for prefix in prefixes), key = len)
            for keyphrase in keyphrases
        ]
    else:
        return [
            ' '.join(
                word for word in keyphrase.split()
                if word.lower() not in nlp.Defaults.stop_words
            ) for keyphrase in keyphrases
        ]


def counter(func):
    """
    Log at info level the time at which the process started 
    and its elapsed system time in seconds, 
    if only the debug flag is set to True.
    """
    if not ai.config.debug:
        return func
    @functools.wraps(func)
    def wrapper_counter(*args, **kwargs):
        started_time = datetime.datetime.now()
        beginning_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        time_delta = end_time - beginning_time
        info_msg = f'{func.__name__}: started on {started_time} (duration: {time_delta} secs)'
        logging.info(info_msg)
        return result
    return wrapper_counter


def get_data_from_ergologic():
    """
    Function which GETs data from the Ergologic backend.
    """
    got_responses = True
    workspaces_url = ERGOLOGIC_WORKSPACES_URL
    discussions_url = ERGOLOGIC_DISCUSSIONS_URL

    response = requests.get(workspaces_url)
    if response.status_code == 200:
        workspaces_json = response.json()
    else:
        got_responses = False
        logging.error(f'The Ergologic backend workspaces url {workspaces_url} was not found!')

    response = requests.get(discussions_url)
    if response.status_code == 200:
        discussions_json = response.json()
    else:
        got_responses = False
        logging.error(f'The Ergologic backend discussions url {discussions_url} was not found!')

    # If we did not receive all respones, early return.
    if not got_responses:
        return

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
