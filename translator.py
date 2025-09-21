# translator.py

import os
import spacy
from dotenv import load_dotenv

# Load any .env vars (if needed elsewhere)
load_dotenv()

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

def question_to_cypher(question: str):
    """
    Convert a natural-language question into a Cypher query.
    """
    doc = nlp(question)
    keyword = next(doc.noun_chunks, None)
    term = keyword.text if keyword else question

    cypher = (
        "MATCH (c:Content) "
        "WHERE toLower(c.text) CONTAINS toLower($term) "
        "RETURN c.text AS answer "
        "LIMIT 5"
    )
    return cypher, {"term": term}