from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from typer import Argument
from ai.utils import (
    counter,
    detect_language,
    remove_punctuation_and_whitespace
)
from ai import config

class ArgumentClassifier:
    english_classifier = None
    greek_classifier = None

    def __init__(self):
        self.__cv = CountVectorizer()
        self.__clf = MultinomialNB()

    def train(self, x, y):
        x_transformed = self.__cv.fit_transform(x)
        self.__clf.fit(x_transformed, y)

    def predict(self, x):
        x_transformed = self.__cv.transform(x)
        return self.__clf.predict(x_transformed)

    def score(self, x, y):
        x_transformed = self.__cv.transform(x)
        return self.__clf.score(x_transformed, y)

    # Suggest different argument types based on documents.
    @staticmethod
    @counter
    def suggest_labels(discussions, lang_det):
        res = []
        for discussion in discussions:
            text = discussion['DiscussionText']
            language = detect_language(lang_det, text)
            text = remove_punctuation_and_whitespace(text)
            if language == 'english':
                predicted = ArgumentClassifier.english_classifier.predict([text])[0]
            elif language == 'greek':
                predicted = ArgumentClassifier.greek_classifier.predict([text])[0]
            else:
                continue

            if predicted != discussion['Position']:
                res.append({
                    'id': discussion['id'],
                    'suggested_argument_type': predicted,
                    'text': discussion['DiscussionText'],
                })
        return {
            'suggested_argument_types': res
        }

    @staticmethod
    @counter
    def train_classifiers(discussions, lang_det):
        english_classifier = ArgumentClassifier()
        greek_classifier = ArgumentClassifier()

        english_texts, english_labels = [], []
        greek_texts, greek_labels = [], []
        for discussion in discussions:
            if discussion['Position'] in ['Issue', 'Solution']:
                continue
            text = discussion['DiscussionText']
            language = detect_language(lang_det, text)
            text = remove_punctuation_and_whitespace(text)
            if language == 'english':
                english_texts.append(text)
                english_labels.append(discussion['Position'])
            elif language == 'greek':
                greek_texts.append(text)
                greek_labels.append(discussion['Position'])

        english_classifier.train(english_texts, english_labels)
        greek_classifier.train(greek_texts, greek_labels)
        ArgumentClassifier.english_classifier = english_classifier
        ArgumentClassifier.greek_classifier = greek_classifier

        if config.debug:
            print(f'English texts accuracy score {ArgumentClassifier.english_classifier.score(english_texts, english_labels)} %')
            print(f'Greek texts accuracy score {ArgumentClassifier.greek_classifier.score(greek_texts, greek_labels)} %')
