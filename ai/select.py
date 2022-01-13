from ai.utils import(
    detect_language, counter, remove_stopwords_from_keyphrases
)
from ai.summarization import (
    run_textrank, keyword_extraction, text_summarization
)


def extract_id_texts_from_communities(database):
    """
    Function that extracts all texts from each,
    joins them, and returns them, in a dictionary,
    which use the community id as a key, and an array of
    ids of all nodes, alongside the joined text as a value.
    """
    query = (
        'MATCH (n:Node)-[:is_similar]-() WHERE EXISTS(n.community) '
        'RETURN n.community, n.Position, COLLECT(DISTINCT n.id), COLLECT(DISTINCT n.DiscussionText)'
    )
    id_texts = database.execute(query, 'r')
    return {
        community: (position, ids, ' '.join(text for text in texts).replace('\n', ' '))
        for community, position, ids, texts in id_texts
    } if id_texts else {}


@counter
def summarize_communities(database, en_nlp, el_nlp, lang_det, top_n, top_sent):
    """
    Function that performs text summarization and keyword
    extraction on all communities, and returns
    these results.
    """
    communities = extract_id_texts_from_communities(database)

    if not communities: # if no communities exist, exit early.
        return {}

    results = {community: None for community in communities.keys()}

    # Iterate each community id and its contents.
    for community, (position, ids, text) in communities.items():

        # Select the nlp object depending on language.
        nlp = (
            en_nlp
            if detect_language(lang_det, text) == 'english' 
            else el_nlp
        )

        # If the community contains no text,
        # or contains no more that 2 documents,
        # then don't summarize it.
        if text == '' or len(ids) < 2:
            continue

        # Run textrank and obtain the processed document.
        doc = run_textrank(text, nlp)

        # Insert the results of both methods into the dict.
        results[community] = [
            position,
            ids,
            text_summarization(doc, nlp, top_n, top_sent),
            keyword_extraction(doc, nlp, top_n)
        ]
    return results
