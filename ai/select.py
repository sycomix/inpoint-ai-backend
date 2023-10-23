from ai.utils import detect_language
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
    return (
        {
            community: (position, ids, ' '.join(texts).replace('\n', ' '))
            for community, position, ids, texts in id_texts
        }
        if id_texts
        else {}
    )


def summarize_communities(database, en_nlp, el_nlp, lang_det, top_n, top_sent):
    """
    Function that performs text summarization on all communities,
    and returns their summaries.
    """
    communities = extract_id_texts_from_communities(database)

    if not communities: # if no communities exist, exit early.
        return {}

    results = {community: None for community in communities.keys()}

    # Iterate each community id and its contents.
    for community, (position, ids, text) in communities.items():

        # If the community contains no text,
        # or contains no more that 2 documents,
        # then don't summarize it.
        if text == '' or len(ids) < 2:
            continue

        # Detect the language of the text.
        language = detect_language(lang_det, text)
        
        # Select the nlp object depending on language.
        nlp = (
            en_nlp
            if language == 'english' 
            else el_nlp
        )

        # Run textrank and obtain the processed document.
        doc = run_textrank(text, nlp)

        # Insert the results of both methods into the dict.
        results[community] = [
            position,
            ids,
            text_summarization(doc, nlp, top_n, top_sent)
        ]
    return results


def aggregate_summaries_keyphrases(workspace, lang_det, en_nlp, el_nlp, top_n, top_sent):
    """
    Function that aggregates summaries from each workspace,
    and produces keyphrases from the aggregated summary.
    """
    # Initialize the results.
    results = {
        'Aggregated': {'Summary': '', 'Keyphrases': []},
    }

    if aggregated_summary := ' '.join(
        summary for item in workspace.values() for summary in item['Summaries']
    ).replace('\n', ' '):
        # Detect the language of the aggregated summary.
        language = detect_language(lang_det, aggregated_summary)

        # Select the nlp object depending on language.
        nlp = (
            en_nlp
            if language == 'english' 
            else el_nlp
        )

        # Run textrank on the aggregated summary.
        doc = run_textrank(aggregated_summary, nlp)

        results['Aggregated'] = {
            'Summary': text_summarization(doc, nlp, top_n, top_sent),
            'Keyphrases': keyword_extraction(doc, nlp, language, 2 * top_n)
        }
    return results
