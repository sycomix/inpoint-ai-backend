from sklearn.decomposition import PCA
from sklearn_extra.cluster import KMedoids
from ai.utils import (
    counter,
    detect_language,
    remove_punctuation_and_whitespace,
    Models
)
from ai import config

from yellowbrick.cluster import KElbowVisualizer
from yellowbrick.cluster import SilhouetteVisualizer
from yellowbrick.text import TSNEVisualizer
from matplotlib import pyplot as plt

class ArgumentClusterer:
    english_clusterer = None
    greek_clusterer = None

    def __init__(self, n_components=30):
        self.__pca = PCA(n_components=n_components, random_state=0)
        self.__clusterer = None
        self.__medoid_texts = {}

    def fit(self, x, output_filename_suffix='output.pdf'):
        x_transformed = self.__pca.fit_transform(x)

        visualizer = KElbowVisualizer(KMedoids(random_state=0), k=(4,12), timings=False, locate_elbow=True)
        visualizer.fit(x_transformed)
        best_n_clusters = visualizer.elbow_value_

        if config.debug:
            visualizer.show(outpath=f'elbow_{output_filename_suffix}')
            plt.clf()

            visualizer = SilhouetteVisualizer(KMedoids(n_clusters=best_n_clusters, random_state=0))
            visualizer.fit(x_transformed)
            visualizer.show(outpath=f'silhouette_{output_filename_suffix}')
            plt.clf()

            clusters = KMedoids(n_clusters=best_n_clusters, random_state=0)
            clusters.fit(x_transformed)
            tsne = TSNEVisualizer(decompose_by=20)
            tsne.fit(x_transformed, ["c{}".format(c) for c in clusters.labels_])
            tsne.show(outpath=f'tsne_{output_filename_suffix}')
            plt.clf()

        self.__clusterer = KMedoids(n_clusters=best_n_clusters, random_state=0)
        self.__clusterer.fit(x_transformed)

    def predict(self, x):
        x_transformed = self.__pca.transform(x)
        return self.__clusterer.predict(x_transformed)

    def get_medoid_indices(self):
        return self.__clusterer.medoid_indices_.tolist()

    # Suggest different argument types based on documents.
    @staticmethod
    @counter
    def suggest_clusters(discussions, lang_det):
        en_nlp, el_nlp, _ = Models.load_models()
        english_clusters = dict.fromkeys(map(str, ArgumentClusterer.english_clusterer.__clusterer.labels_), {'nodes': [], 'texts': []})
        greek_clusters =  dict.fromkeys(map(str, ArgumentClusterer.greek_clusterer.__clusterer.labels_), {'nodes': [], 'texts': []})

        for discussion in discussions:
            text = discussion['DiscussionText']
            language = detect_language(lang_det, text)
            text = remove_punctuation_and_whitespace(text)
            if language == 'english':
                predicted = ArgumentClusterer.english_clusterer.predict([en_nlp.tokenizer(text).vector])[0]
                english_clusters[str(predicted)]['nodes'].append(discussion['id'])
                english_clusters[str(predicted)]['texts'].append(text)
            elif language == 'greek':
                predicted = ArgumentClusterer.greek_clusterer.predict([el_nlp.tokenizer(text).vector])[0]
                greek_clusters[str(predicted)]['nodes'].append(discussion['id'])
                greek_clusters[str(predicted)]['texts'].append(text)

        return {
            'greek_clusters': greek_clusters,
            'english_clusters': english_clusters,
            'greek_medoid_texts': ArgumentClusterer.greek_clusterer.__medoid_texts,
            'english_medoid_texts': ArgumentClusterer.english_clusterer.__medoid_texts,
        }

    @staticmethod
    @counter
    def fit_clusterers(discussions, lang_det):
        english_clusterer = ArgumentClusterer()
        greek_clusterer = ArgumentClusterer()

        english_texts = []
        greek_texts = []
        for discussion in discussions:
            if discussion['Position'] in ['Issue']:
                continue
            text = discussion['DiscussionText']
            language = detect_language(lang_det, text)
            text = remove_punctuation_and_whitespace(text)
            if language == 'english':
                english_texts.append(text)
            elif language == 'greek':
                greek_texts.append(text)

        en_nlp, el_nlp, _ = Models.load_models()
        english_embeddings = [en_nlp.tokenizer(text).vector for text in english_texts]
        english_clusterer.fit(english_embeddings, 'english.pdf')
        greek_embeddings = [el_nlp.tokenizer(text).vector for text in greek_texts]
        greek_clusterer.fit(greek_embeddings, 'greek.pdf')

        for i in english_clusterer.__clusterer.medoid_indices_:
            english_clusterer.__medoid_texts[str(english_clusterer.__clusterer.labels_[i])] = english_texts[i]
        for i in greek_clusterer.__clusterer.medoid_indices_:
            greek_clusterer.__medoid_texts[str(greek_clusterer.__clusterer.labels_[i])] = greek_texts[i]

        ArgumentClusterer.english_clusterer = english_clusterer
        ArgumentClusterer.greek_clusterer = greek_clusterer