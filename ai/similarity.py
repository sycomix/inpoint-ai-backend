from itertools import product # Cartesian
from spacy.language import Language
from spacy.tokens import Doc
from ai.utils import (
    detect_language, preprocess
)


def textual_similarity(nlp, language, source, target):
    """
    Function which compares two lists of texts
    (source & target) of a certain language, 
    using the associated nlp pipeline object.
    """
    
    # Apply preprocessing to all documents.
    source_texts = [preprocess(text, nlp, language) for (_, text, language) in source]
    target_texts = [preprocess(text, nlp, language) for (_, text, language) in target]

    # Set a custom extension for documents.
    Doc.set_extension('neo4j_id', default = -1, force = True)

    # Create all document objects using the NLP pipe.
    source_docs = list(nlp.pipe(source_texts))
    target_docs = list(nlp.pipe(target_texts))

    # Assign all ids, at their associated document objects.
    for (i, source_doc), (j, target_doc) in zip(enumerate(source_docs), 
                                                enumerate(target_docs)):
        source_doc._.neo4j_id = source[i][0]
        target_doc._.neo4j_id = source[j][0]
    
    # Compare all texts for similarity.
    # For two docs list of size n, the comparison is Θ(n^2).
    # However, this function was also build for single text comparison
    # with a list of texts, which makes it Θ(n) in that case.

    similarity_pairs = [(
        min(element[0]._.neo4j_id, element[1]._.neo4j_id),
        round(element[0].similarity(element[1]), 2),
        max(element[0]._.neo4j_id, element[1]._.neo4j_id),
        )
        for element in product(source_docs, target_docs)
        if element[0]._.neo4j_id != element[1]._.neo4j_id
    ]

    # Return unique non-duplicate pairs.
    return list(set(similarity_pairs))


def calc_similarity_pairs(text_ids, en_nlp, el_nlp, lang_det, cutoff):
    """
    This function splits the list of texts into greek and english,
    then calculates the similarity pairs for each language, if possible.
    """

    # Not enough texts to compare; return early.
    if len(text_ids) < 2:
        return []

    # Detect the language for each text and assign it.
    texts = [(id, text, detect_language(lang_det, text)) for (id, text) in text_ids]

    # Split the texts between english and greek.
    en_texts = [text for text in texts if text[2] == 'english']
    el_texts = [text for text in texts if text[2] == 'greek']

    # Calculate all textual similarity pairs.
    sim_pairs_en = (
        textual_similarity(en_nlp, 'english', en_texts, en_texts)
        if len(en_texts) >= 2 else []
    )

    sim_pairs_el = (
        textual_similarity(el_nlp, 'greek', el_texts, el_texts) 
        if len(el_texts) >= 2 else []
    )
    
    return [
        sim_pair 
        for sim_pair in sim_pairs_en + sim_pairs_el
        if sim_pair[1] >= cutoff
    ]
