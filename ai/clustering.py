import numpy as np
from sklearn.decomposition import PCA
from sklearn_extra.cluster import KMedoids
from ai.utils import (
    detect_language,
    remove_punctuation_and_whitespace
)
from ai.summarization import (
    run_textrank, text_summarization
)
from ai import config
from yellowbrick.cluster import KElbowVisualizer
from yellowbrick.cluster import SilhouetteVisualizer
from yellowbrick.text import TSNEVisualizer
from matplotlib import pyplot as plt


class ArgumentClusterer:
    english_clusterer, greek_clusterer = None, None

    def __init__(self, n_components = 2):
        #self.__pca = PCA(n_components = n_components, random_state = 0)
        self.__clusterer = None
        self.__medoid_texts = None

    def fit(self, x, output_filename_suffix = 'output.pdf'):
        x = np.array(x)
        num_samples, num_features = x.shape[0], x.shape[1]
        self.__pca = PCA(n_components = min(num_samples, num_features), random_state=0)
        x_transformed = self.__pca.fit_transform(x)

        visualizer = KElbowVisualizer(KMedoids(random_state = 0), k = (1, num_samples), timings = False, locate_elbow = True)
        visualizer.fit(x_transformed)
        best_n_clusters = visualizer.elbow_value_ if visualizer.elbow_value_ is not None else 1

        self.__clusterer = KMedoids(n_clusters = best_n_clusters, random_state = 0)
        self.__clusterer.fit(x_transformed)

    def predict(self, x):
        x_transformed = self.__pca.transform(x)
        return self.__clusterer.predict(x_transformed)

    def get_medoid_indices(self):
        return self.__clusterer.medoid_indices_.tolist()

    # Sort different arguments into similar clusters.
    @staticmethod
    def suggest_clusters(discussions, lang_det, en_nlp, el_nlp):

        # If the workspace does not have enough discussions, early exit.
        if len(discussions) < 3:
            return {
                'greek_clusters': {},
                'english_clusters': {}
            }
        
        # Fit all clusterers for all discussions of a single workspace.
        ArgumentClusterer.fit_clusterers(discussions, lang_det, en_nlp, el_nlp)
        english_clusters = {
            label: {'nodes': [], 'texts': [], 'summary': '', 'medoid_text': ''} 
            for label in map(str, ArgumentClusterer.english_clusterer.__clusterer.labels_)
        } if ArgumentClusterer.english_clusterer is not None else {}
        greek_clusters =  {
            label: {'nodes': [], 'texts': [], 'summary': '', 'medoid_text': ''} 
            for label in map(str, ArgumentClusterer.greek_clusterer.__clusterer.labels_)
        } if ArgumentClusterer.greek_clusterer is not None else {}

        for discussion in discussions:

            if discussion['Position'] in ['Issue', 'Solution']:
                continue

            text = discussion['DiscussionText']
            language = detect_language(lang_det, text)
            text = remove_punctuation_and_whitespace(text)

            if language == 'english':
                if ArgumentClusterer.english_clusterer is None:
                    continue
                predicted = str(ArgumentClusterer.english_clusterer.predict([en_nlp.tokenizer(text).vector])[0])
                english_clusters[predicted]['nodes'].append(discussion['id'])
                english_clusters[predicted]['texts'].append(text)
                english_clusters[predicted]['medoid_text'] = ArgumentClusterer.english_clusterer.__medoid_texts[predicted]
            elif language == 'greek':
                if ArgumentClusterer.greek_clusterer is None:
                    continue
                predicted = str(ArgumentClusterer.greek_clusterer.predict([el_nlp.tokenizer(text).vector])[0])
                greek_clusters[predicted]['nodes'].append(discussion['id'])
                greek_clusters[predicted]['texts'].append(text)
                greek_clusters[predicted]['medoid_text'] = ArgumentClusterer.greek_clusterer.__medoid_texts[predicted]

        # Run textrank on non-empty aggregated text from each cluster for each language.
        for en_cluster in english_clusters.keys():
            en_text = '. '.join(english_clusters[en_cluster]['texts'])
            if en_text != '':
                en_doc = run_textrank(en_text, en_nlp)
                english_clusters[en_cluster]['summary'] = text_summarization(en_doc, en_nlp, config.top_n, config.top_sent)
            del english_clusters[en_cluster]['texts']

        for el_cluster in greek_clusters.keys():
            el_text = '. '.join(greek_clusters[el_cluster]['texts'])
            if el_text != '':
                el_doc = run_textrank(el_text, el_nlp)
                greek_clusters[el_cluster]['summary'] = text_summarization(el_doc, el_nlp, config.top_n, config.top_sent)
            del greek_clusters[el_cluster]['texts']

        return {
            'greek_clusters': greek_clusters,
            'english_clusters': english_clusters
        }

    @staticmethod
    def fit_clusterers(discussions, lang_det, en_nlp, el_nlp):
        english_clusterer, greek_clusterer = None, None
        english_texts, greek_texts = [], []

        for discussion in discussions:
            if discussion['Position'] in ['Issue', 'Solution']:
                continue
            text = discussion['DiscussionText']
            language = detect_language(lang_det, text)
            text = remove_punctuation_and_whitespace(text)
            if language == 'english':
                english_texts.append(text)
            elif language == 'greek':
                greek_texts.append(text)

        if len(english_texts) > 2:
            # Initialize the English Clusterer.
            english_clusterer = ArgumentClusterer()

            # Calculate the embeddings for each text of this discussion.
            english_embeddings = [en_nlp.tokenizer(text).vector for text in english_texts]

            # Fit the clusterer using the textual embeddings of this discussion.
            english_clusterer.fit(english_embeddings, 'english.pdf')

            # Find the medoids of each cluster from each language.
            english_clusterer.__medoid_texts = {
                str(english_clusterer.__clusterer.labels_[i]): english_texts[i]
                for i in english_clusterer.__clusterer.medoid_indices_
            }

        if len(greek_texts) > 2:
            # Initialize the Greek Clusterer.
            greek_clusterer = ArgumentClusterer()

            # Calculate the embeddings for each text of this discussion.
            greek_embeddings = [el_nlp.tokenizer(text).vector for text in greek_texts]

            # Fit the clusterer using the textual embeddings of this discussion.
            greek_clusterer.fit(greek_embeddings, 'greek.pdf')

            # Find the medoids of each cluster from each language.
            greek_clusterer.__medoid_texts = {
                str(greek_clusterer.__clusterer.labels_[i]): greek_texts[i]
                for i in greek_clusterer.__clusterer.medoid_indices_
            }

        ArgumentClusterer.english_clusterer = english_clusterer
        ArgumentClusterer.greek_clusterer = greek_clusterer
