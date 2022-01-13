import pytextrank
from ai.utils import remove_stopwords_from_keyphrases


def run_textrank(text, nlp):
    """
    Function that calculates textrank,
    for a single document. It serves as a basis
    as to not rerun textrank for both functions below.
    """
    # Temporarily add PyTextRank to the spaCy pipeline.
    nlp.add_pipe('textrank', last = True)

    # Create the document using the pipeline.
    doc = nlp(text)
    
    # Remove textrank from the pipeline.
    nlp.remove_pipe('textrank')

    return doc


def keyword_extraction(doc, nlp, top_n = 10, remove_stopwords = False):
    """
    Function that extracts the top_n most significant
    keywords, using textrank. The algorithm is implemented
    as a highly performant spacy pipeline component.
    """

    # Extract the top N phrases from the document.
    keyphrases = [
        phrase.text for phrase in doc._.phrases 
        if phrase.text.lower() not in nlp.Defaults.stop_words
    ][:top_n]
    
    # Remove stopwords included in the keyphrases.
    if remove_stopwords:
        keyphrases = remove_stopwords_from_keyphrases(keyphrases, nlp)

    return keyphrases


def text_summarization(doc, nlp, top_n = 15, top_sent = 5):
    """
    Function that extracts the top_sent most significant
    sentences, using textrank. The algorithm is implemented
    as a highly performant spacy pipeline component.
    """

    # Access the textrank component to perform summarization.
    summary = '\n'.join(sent.text
        for sent in doc._.textrank.summary(
            limit_phrases = top_n, 
            limit_sentences = top_sent)
    )

    return summary
